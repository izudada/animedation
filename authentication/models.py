from django.contrib.auth.models import AbstractUser
from django.db import models

from authentication.managers import UserManager
from helpers.db_utils import BaseModel


class User(BaseModel, AbstractUser ):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email