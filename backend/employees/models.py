from django.db import models
from django.conf import settings

class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    emp_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()

    department = models.CharField(max_length=100)
    role = models.CharField(max_length=100)

    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_joined = models.DateField()

    is_active = models.BooleanField(default=True)  # ✅ SOFT DELETE

    def __str__(self):
        return f"{self.emp_code} - {self.name}"
