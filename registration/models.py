from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    base_currency = models.DecimalField(default=0.0, decimal_places=2, max_digits=19)
