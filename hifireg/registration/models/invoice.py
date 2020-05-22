from django.db import models
from datetime import datetime
 
class Invoice(models.Model):
   amount = models.PositiveIntegerField()
   due_date = models.DateTimeField(default=datetime.now())
   order = models.ForeignKey('Order', on_delete=models.CASCADE)