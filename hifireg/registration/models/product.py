from django.db.models import Sum, F, Case, When, Value, OuterRef, Subquery, Exists
from django.db.models.functions import Coalesce
from django.db import models
from django.contrib.postgres.aggregates import ArrayAgg

from .registration import OrderItem


class ProductManager(models.Manager):
    def get_product_info_for_user(self, user):
        pending_order_items = OrderItem.objects.filter(order__registration__user=user, order__session__isnull=False, product=OuterRef('pk'))
        purchased_order_items = OrderItem.objects.filter(order__registration__user=user, order__session__isnull=True, product=OuterRef('pk'))
        all_other_products_for_user = OrderItem.objects.filter(order__registration__user=user).exclude(product=(OuterRef(OuterRef('pk')))).values('product')
        conflicts_with_order = ProductSlot.objects.filter(is_exclusionary=True, product=OuterRef('pk')).filter(product__in=Subquery(all_other_products_for_user))
        conflicts_with_order_agg = ProductSlot.objects.filter(is_exclusionary=True, product=OuterRef('pk')).filter(product__in=Subquery(all_other_products_for_user)).values('product').annotate(pks=ArrayAgg('pk')).values('pks')
        all_order_items_for_product = OrderItem.objects.filter(product=OuterRef('pk')).order_by().values('product').annotate(total=Sum('quantity')).values('total')
        return self.filter(is_visible=True).\
            annotate(quantity_purchased=Coalesce(Sum(Subquery(purchased_order_items.values('quantity'))), 0)).\
            annotate(quantity_claimed=Coalesce(Subquery(pending_order_items.values('quantity')[:1]), 0)).\
            annotate(quantity_available=F('total_quantity') - Coalesce(Subquery(all_order_items_for_product), 0)).\
            annotate(exclusionary_slot_exists_in_order=Exists(conflicts_with_order)).\
            annotate(slot_conflicts=Coalesce(Subquery(conflicts_with_order_agg), []))


class ProductCategory(models.Model):
    DANCE = 'DANCE'
    CLASS = 'CLASS'
    SHOWCASE = 'SHWCS'
    MERCH = 'MERCH'
    SECTION_CHOICES = [
        (DANCE, 'Dance Passes'),
        (CLASS, 'Class Passes'),
        (SHOWCASE, 'Showcase Admission'),
        (MERCH, 'Merchandise')
    ]
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=5, choices=SECTION_CHOICES)
    is_slot_based = models.BooleanField(default=True)
    rank = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class ProductSlot(models.Model):
    name = models.CharField(max_length=100)
    is_exclusionary = models.BooleanField(default=True)
    rank = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Product(models.Model):
    slots = models.ManyToManyField(ProductSlot)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT)
    total_quantity = models.PositiveIntegerField()
    max_quantity_per_reg = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    price = models.PositiveIntegerField()
    is_compable = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    is_ap_eligible = models.BooleanField(default=True)

    objects = ProductManager()

    def __str__(self):
        return self.title

    @property
    def available_quantity(self):
        return self.total_quantity - (self.orderitem_set.aggregate(Sum('quantity'))['quantity__sum'] or 0)
