from django.db import models

class Employee(models.Model):
    emp_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)

    # Correct status field with proper choices
    status = models.CharField(
        max_length=20,
        choices=[
            ("Active", "Active"),
            ("Inactive", "Inactive")
        ],
        default="Active"
    )

    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_joined = models.DateField()

    def __str__(self):
        return f"{self.emp_code} - {self.name}"
