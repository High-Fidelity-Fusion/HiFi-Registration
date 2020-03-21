from django.db import models
from django.contrib.sessions.models import Session
from django.db import transaction, IntegrityError
from django.core.exceptions import SuspiciousOperation
from django.db.models import Sum
from .validators import validate_agree

class UserSession(models.Model):
    DjangoSession = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)

    def get_current_id():
        if UserSession.get_current() is not None:
            return UserSession.get_current().id
        return None

    def get_current():
        return UserSession.objects.first() #TODO update to get the actual current UserSession based on the current DjangoSession

class Product(models.Model):
    total_quantity = models.PositiveIntegerField()
    max_quantity_per_reg = models.PositiveIntegerField()
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    price = models.PositiveIntegerField()

    @property
    def available_quantity(self):
        return self.total_quantity - self.orderitem_set.quantity__sum

class Registration(models.Model):
    agree_to_coc = models.BooleanField(verbose_name="Do you agree to the Code of Conduct?", null=True, blank=False)
    allergens_severe = models.TextField(verbose_name="Severe Allergies", help_text="List allergens that would be a threat to you if they were in the venue at all", max_length=1000, null=True, blank=False)

    @property
    def is_submitted(self):
        return self.order_set.exists(is_submitted=True)

    @property
    def is_accessible_pricing(self):
        return self.order_set.exists(is_accessible_pricing=True)

class Order(models.Model):
    user_session = models.OneToOneField(UserSession, on_delete=models.CASCADE, null=True, default=UserSession.get_current_id)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    final_price = models.PositiveIntegerField(default=0)

    @property
    def original_price(self):
        return self.orderitem_set.aggregate(Sum('original_price'))['original_price__sum']

    @property
    def price_after_discounts(self):
        return self.orderitem_set.price_after_discounts__sum

    @property
    def is_submitted(self):
        return self.user_session is None

    @property
    def is_accessible_pricing(self):
        return self.price_after_discounts > self.final_price

    def add_item(self, product, quantity):
        if self.is_submitted or self.is_accessible_pricing:
            raise SuspiciousOperation("You cannot add items to a finalized order.")

        operation_succeeded = False
        try:
            with transaction.atomic():
                if product.available_quantity > quantity:
                    order_item = self.orderitem_set.get_or_create(product=product)
                    order_item.original_unit_price = product.price
                    order_item.increment(quantity)
            operation_succeeded = True
        except IntegrityError:
            operation_succeeded = False

        if operation_succeeded:
            self.final_price = self.price_after_discounts
            if self.registration.is_accessible_pricing:
                self.final_price = 0

        return operation_succeeded

    @transaction.atomic
    def remove_item(self, product, quantity):
        self.orderitem_set.get(product=product).decrement(quantity)

    @transaction.atomic
    def claim_accessible_pricing(self):
        if APFund.get_available_funds() > self.final_price:
            self.final_price = 0
            return True
        return False


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    original_unit_price = models.PositiveIntegerField(null=True)
    quantity = models.PositiveIntegerField(default=0)

    @property
    def price_after_discounts(self):
        return self.unit_price_after_discounts * self.quantity

    @property
    def unit_price_after_discounts(self):
        return self.original_unit_price
        #TODO impl discounts using self.product.price_after_discounts(self.order.registration)

    @property
    def original_price(self):
        return self.original_unit_price * self.quantity

    def increment(self, quantity):
        self.quantity += quantity

    def decrement(self, quantity):
        self.quantity -= quantity
        if self.order.final_price > self.order.price_after_discounts - (quantity * self.unit_price_after_discounts):
            self.order.final_price = self.order.price_after_discounts - (quantity * self.unit_price_after_discounts)
        if self.quantity < 1:
            self.delete()

class APFund(models.Model):
    contribution = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=200)
    last_updated = models.TimeField(auto_now=True)

    @transaction.atomic
    def get_available_funds():
        return APFund.objects.aggregate(Sum('contribution'))['contribution__sum'] - Order.objects.aggregate(Sum('ap_amount_waived'))['ap_amount_waived__sum']


