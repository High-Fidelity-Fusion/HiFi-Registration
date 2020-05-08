from django.db import models

class ProductSlot(models.Model):
    name = models.CharField(max_length=100)
    is_exclusionary = models.BooleanField(default=True)
    rank = models.PositiveIntegerField()

    def __str__(self):
        return self.name