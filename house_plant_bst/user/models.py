from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Custom user model"""

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    location = models.CharField(max_length=10)
    badges = models.IntegerField(default=0)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name',
        'location',
    ]

    def __str__(self):
        return self.username
