from django.db import models
from datetime import datetime

class Invoice(models.Model):
   amount = models.PositiveIntegerField()
   due_date = models.DateTimeField()
   order = models.ForeignKey('Order', on_delete=models.CASCADE)
   pay_at_checkout = models.BooleanField(default=False)
