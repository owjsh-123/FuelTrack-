from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    email=models.EmailField(unique=True)
    reputation=models.IntegerField(default=0)
    country_code=models.CharField(max_length=2,default='CA')
    USERNAME_FIELD='email'; REQUIRED_FIELDS=['username']
