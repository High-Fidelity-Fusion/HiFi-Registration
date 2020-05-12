from django.core.exceptions import SuspiciousOperation
from django.db import models
from django.db import transaction
from django.contrib.sessions.models import Session
from django.db.models import Sum
from .product import Product
from .registration import Registration
from.ap_fund import APFund

class Order(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, null=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    original_price = models.PositiveIntegerField(default=0)
    accessible_price = models.PositiveIntegerField(default=0)
    stretch_price = models.PositiveIntegerField(default=0)

    @property
    def is_submitted(self):
        return self.session is None

    @property
    def is_accessible_pricing(self):
        return self.original_price > self.accessible_price

    @property
    def ap_eligible_amount(self):
        return self.orderitem_set.filter(product__is_ap_eligible=True).aggregate(Sum('total_price'))['total_price__sum'] or 0

    def add_item(self, product_id, quantity):
        product = Product.objects.get(pk=product_id)
        if self.is_submitted:
            raise SuspiciousOperation('You cannot add items to a finalized order.')
        for slot in product.slots.iterator():
            if slot.is_exclusionary == True and self.orderitem_set.exclude(product=product).filter(product__slots=slot).exists():
                raise SuspiciousOperation('You cannot have more than one product in an exclusionary slot.')
        if (self.orderitem_set.get(product=product).quantity if self.orderitem_set.filter(product=product).exists() else 0) + quantity > product.max_quantity_per_reg:
            raise SuspiciousOperation('You cannot exceed the max quantity per registration for that product.')


        with transaction.atomic():
            product = Product.objects.filter(pk=product_id).select_for_update().get()
            if product.available_quantity >= quantity:
                order_item, created = self.orderitem_set.get_or_create(product = product,
                                                                       defaults={'unit_price': 0 if self.registration.is_comped and product.is_compable else product.price})
                order_item.increment(quantity)
                product.available_quantity = product.available_quantity - quantity
                product.save()

                self.original_price = self.orderitem_set.aggregate(Sum('total_price'))['total_price__sum']
                self.accessible_price = self.original_price
                self.save()
                return True
            return False

    @transaction.atomic
    def remove_item(self, product_id, quantity):
        product = Product.objects.filter(pk=product_id).select_for_update().get()
        product.available_quantity = product.available_quantity + quantity
        product.save()
        self.orderitem_set.get(product=product).decrement(quantity)
        self.original_price = self.orderitem_set.aggregate(Sum('total_price'))['total_price__sum'] or 0
        if self.original_price < self.accessible_price:
            self.accessible_price = self.original_price
        self.save()

    @transaction.atomic
    def claim_accessible_pricing(self):
        Order.objects.select_for_update()
        if self.get_available_ap_funds() >= self.ap_eligible_amount:
            self.accessible_price = self.original_price - self.ap_eligible_amount
            self.save()
            return True
        return False

    @classmethod
    def get_available_ap_funds(cls):
        return (APFund.objects.aggregate(Sum('contribution'))['contribution__sum'] or 0) \
               - (cls.objects.aggregate(disbursed_amount=Sum('original_price') - Sum('accessible_price'))['disbursed_amount'] or 0)

    @classmethod
    def for_user(cls, user):
        return Registration.for_user(user).order_set.get(session__isnull=False)