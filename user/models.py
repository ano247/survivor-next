from django.contrib.auth.models import AbstractUser
from django.db import models

from user.managers import CustomUserManager


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='email address'
    )

    user_token = models.CharField(
        max_length=64,
        primary_key=True,
    )

    device_token = models.CharField(
        blank=True,
        max_length=64,
    )

    objects = CustomUserManager()


class Survivor(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )


class Advocate(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    type = models.CharField(
        max_length=64,
        default='police',
    )
