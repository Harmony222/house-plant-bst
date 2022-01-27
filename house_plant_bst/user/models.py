from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """Custom user manager"""

    def create_user(
        self, username, password, email, first_name, last_name, location
    ):
        """Creates and saves a new user"""
        if (
            not username
            or not email
            or not first_name
            or not last_name
            or not location
        ):
            raise ValueError(
                '''Users must have a valid username, password, email address,
                first name, last name, and location'''
            )
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            location=location,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    """Custom user model"""

    username = models.CharField(max_length=150, unique=True, blank=False)
    email = models.EmailField(max_length=254, blank=False)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    location = models.CharField(max_length=10, blank=False)
    badges = models.IntegerField(default=0, blank=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name',
        'location',
    ]

    def __str__(self):
        return self.username
