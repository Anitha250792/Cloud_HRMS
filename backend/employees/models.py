from django.db import models
from django.conf import settings

class Employee(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # BASIC INFO

    emp_code = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    dob = models.DateField(
        null=True,
        blank=True
    )

    marital_status = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    address = models.TextField(
        blank=True,
        null=True
    )
    emergency_contact = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    # EMPLOYMENT

    department = models.CharField(
        max_length=100
    )

    role = models.CharField(
        max_length=100
    )

    designation = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    employment_type = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    reporting_manager = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    date_joined = models.DateField()

    # PAYROLL

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    bank_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    bank_account = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    ifsc_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    pan_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    pf_number = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    # SYSTEM

    profile_photo = models.ImageField(
        upload_to="employees/",
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.emp_code} - {self.name}"