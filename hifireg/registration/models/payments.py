from django.db import models
 
class Payments(models.Model):
   amount = models.PositiveIntegerField()
   date = models.DateTimeField()
   registration = models.ForeignKey('Registration', on_delete=models.SET_NULL, null=True)