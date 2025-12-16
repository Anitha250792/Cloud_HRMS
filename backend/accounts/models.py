from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, name="", role="EMPLOYEE"):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name,
            role=role,
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, name="Admin"):
        user = self.create_user(
            email=email,
            password=password,
            name=name,
            role="HR",   # 🔴 SUPERUSER SHOULD BE HR
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("EMPLOYEE", "Employee"),
        ("HR", "HR Admin"),
    )

    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="EMPLOYEE")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 🔐 IMPORTANT
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.email
