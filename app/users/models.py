from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from common.models import CommonModel


class UserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError("Please enter your email address")

        user = self.model(email=email)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)

        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, CommonModel):
    email = models.EmailField(max_length=255, unique=True, editable=False)
    name = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self) -> str:
        return f"name: {self.name}"
