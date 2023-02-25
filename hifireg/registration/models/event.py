from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=10, primary_key=True)
    policies = models.TextField(null=True, blank=True)
    requires_vaccination = models.BooleanField()