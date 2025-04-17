from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass

class SuperUserManger(models.Manager):
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        return qs.filter(is_superuser=True)

class SuperUser(User):
    objects = SuperUserManger()
    
    class Meta:
        proxy=True
        
    def save(self, *args, **kwargs):
        self.is_superuser = True
        super().save(*args, **kwargs)