from django.db import models


class APFund(models.Model):
    contribution = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=200)
    last_updated = models.TimeField(auto_now=True)
