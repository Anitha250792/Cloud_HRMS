from django.db import models
from django.conf import settings
from employees.models import Employee

class Leave(models.Model):
    LEAVE_TYPES = [
        ("CASUAL", "Casual Leave"),
        ("SICK", "Sick Leave"),
        ("EARNED", "Earned Leave"),
        ("UNPAID", "Unpaid Leave"),
    ]

    STATUS_CHOICES = [  
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leaves"
    )

    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    applied_on = models.DateTimeField(auto_now_add=True)

    def total_days(self):
        return (self.end_date - self.start_date).days + 1
