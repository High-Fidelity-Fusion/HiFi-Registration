from django.db import models
from django.contrib.sessions.models import Session

class UserSession(models.Model):
    DjangoSession = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)

    def get_current_id():
        return UserSession.get_current().id

    def get_current():
        return UserSession.objects.first() #TODO update to get the actual current UserSession based on the current DjangoSession

class Registration(models.Model):
    agree_to_coc = models.BooleanField(verbose_name="Do you agree to the Code of Conduct?", null=True, blank=False)
    allergens_severe = models.TextField(verbose_name="Severe Allergies", help_text="List allergens that would be a threat to you if they were in the venue at all", max_length=828, null=True, blank=False)

    @property
    def is_submitted(self):
        return self.order_set.exists(is_submitted=True)

class Order(models.Model):
    user_session = models.OneToOneField(UserSession, on_delete=models.CASCADE, null=True, default=UserSession.get_current_id)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    final_price = models.PositiveIntegerField(default=0)

    @property
    def original_price(self):
        return self.orderitem_set.original_price__sum

    @property
    def price_after_discounts(self):
        return self.orderitem_set.price_after_discounts__sum

    @property
    def is_submitted(self):
        return self.user_session is None

    @property
    def is_accessible_pricing(self):
        return self.final_price < self.price_after_discounts


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    original_unit_price = models.PositiveIntegerField()
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

    def decrement(self):
        if self.order.final_price > self.order.price_after_discounts - self.unit_price_after_discounts:
            self.order.final_price = self.order.price_after_discounts - self.unit_price_after_discounts

        self.quantity -= 1
        if self.quantity < 1:
            self.delete()

