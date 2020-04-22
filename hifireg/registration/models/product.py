from django.db.models import Sum, F, Case, When, Value, OuterRef, Subquery, Exists
from django.db.models.functions import Coalesce
from django.db import models

from .registration import OrderItem


class ProductManager(models.Manager):
    def get_product_info_for_user(self, user):
        pending_order_items = OrderItem.objects.filter(order__registration__user=user, order__session__isnull=False, product=OuterRef('pk'))
        purchased_order_items = OrderItem.objects.filter(order__registration__user=user, order__session__isnull=True, product=OuterRef('pk'))
        all_products_for_user = OrderItem.objects.filter(order__registration__user=user).values('product')
        conflicts_with_order = ProductSlot.objects.filter(is_exclusionary=True, product=OuterRef('pk')).filter(product__in=Subquery(all_products_for_user))
        all_order_items_for_product = OrderItem.objects.filter(product=OuterRef('pk')).order_by().values('product').annotate(total=Sum('quantity')).values('total')
        return self.filter(is_visible=True).\
            annotate(quantity_purchased=Coalesce(Sum(Subquery(purchased_order_items.values('quantity'))), 0)).\
            annotate(quantity_claimed=Coalesce(Subquery(pending_order_items.values('quantity')[:1]), 0)).\
            annotate(quantity_available=F('total_quantity') - Coalesce(Subquery(all_order_items_for_product), 0)).\
            annotate(exclusionary_slot_exists_in_order=Exists(conflicts_with_order))


class ProductCategory(models.Model):
    DANCE = 'DANCE'
    CLASS = 'CLASS'
    ADD_ON = 'ADDON'
    SECTION_CHOICES = [
        (DANCE, 'Dance Passes'),
        (CLASS, 'Class Passes'),
        (ADD_ON, 'Add-Ons')
    ]
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=5, choices=SECTION_CHOICES)
    is_slot_based = models.BooleanField(default=True)
    rank = models.PositiveIntegerField()


class ProductSlot(models.Model):
    name = models.CharField(max_length=100)
    is_exclusionary = models.BooleanField(default=True)
    rank = models.PositiveIntegerField()


class Product(models.Model):
    slots = models.ManyToManyField(ProductSlot)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT)
    total_quantity = models.PositiveIntegerField()
    max_quantity_per_reg = models.PositiveIntegerField()
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    price = models.PositiveIntegerField()
    is_compable = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    is_ap_eligible = models.BooleanField(default=True)

    objects = ProductManager()

    @property
    def available_quantity(self):
        return self.total_quantity - (self.orderitem_set.aggregate(Sum('quantity'))['quantity__sum'] or 0)
