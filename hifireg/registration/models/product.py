from django.db import models
from django.db import transaction
from django.db.models import Sum
from .product_manager import ProductManager
from django.utils.timezone import now
from django.core.exceptions import ValidationError

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
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=5, choices=SECTION_CHOICES)
    is_slot_based = models.BooleanField(default=True)
    rank = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Product(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    slots = models.ManyToManyField('ProductSlot', blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT)
    total_quantity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField()
    max_quantity_per_reg = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField()
    is_compable = models.BooleanField(default=False)
    is_ap_eligible = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True, validators=[])

    objects = ProductManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.available_quantity = self.total_quantity
        super().save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({'end_date': 'End date must be after Start date.'})
        super().clean(*args, **kwargs)

    @classmethod
    @transaction.atomic
    def sync_available_quantity(cls):
        for product in cls.objects.select_for_update().iterator():
            product.available_quantity = product.total_quantity - (product.orderitem_set.aggregate(Sum('quantity'))['quantity__sum'] or 0)
            product.save()
