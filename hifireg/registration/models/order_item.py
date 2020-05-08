from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db.models import F

class OrderItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    unit_price = models.PositiveIntegerField(null=True)
    total_price = models.PositiveIntegerField(null=True)
    quantity = models.PositiveIntegerField(default=0)

    def increment(self, quantity):
        self.quantity += quantity
        self.total_price = self.unit_price * self.quantity
        self.save()

    def decrement(self, quantity):
        self.quantity -= quantity
        self.total_price = self.unit_price * self.quantity
        self.save()
        if self.quantity < 1:
            self.delete()

@receiver(pre_delete, sender=OrderItem, dispatch_uid='decrement_quantity_on_delete')
def decrement_quantity_on_delete(sender, instance, using, **kwargs):
    product = instance.product
    product.available_quantity = F('available_quantity') + instance.quantity
    product.save()
