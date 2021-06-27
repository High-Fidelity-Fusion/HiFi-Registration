from django.db import models


class APFund(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    contribution = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=200)
    last_updated = models.TimeField(auto_now=True)
