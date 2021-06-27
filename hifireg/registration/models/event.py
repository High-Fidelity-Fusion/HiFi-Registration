from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=10, primary_key=True)