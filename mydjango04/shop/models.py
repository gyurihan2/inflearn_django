from django.db import models

# Create your models here.
class ZipCode(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)