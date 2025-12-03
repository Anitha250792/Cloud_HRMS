from django.db import models
from employees.models import Employee
from datetime import timedelta

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} | {self.date}"

    def total_hours(self):
        if self.check_in and self.check_out:
            return self.check_out - self.check_in
        return timedelta(0)
