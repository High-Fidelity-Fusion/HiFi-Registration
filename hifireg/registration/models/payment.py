from django.db import models
 
class Payment(models.Model):
   amount = models.PositiveIntegerField()
   date = models.DateTimeField(auto_now_add=True)
   registration = models.ForeignKey('Registration', on_delete=models.SET_NULL, null=True)