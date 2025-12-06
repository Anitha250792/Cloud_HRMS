from django.db import models
from employees.models import Employee

class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    month = models.IntegerField()
    year = models.IntegerField()

    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    working_days = models.IntegerField(default=30)
    present_days = models.IntegerField(default=0)

    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Calculate gross salary
        self.gross_salary = float(self.basic_salary)

        # Salary per day
        per_day = float(self.basic_salary) / self.working_days

        # Loss of pay
        lop = self.working_days - int(self.present_days)

        # Net salary calculation
        net = float(self.basic_salary) - (per_day * lop)

        self.net_salary_value = round(net, 2)

        super().save(*args, **kwargs)

    @property
    def net_salary(self):
        """Return correct net salary for serializer."""
        return float(self.net_salary_value)

    def __str__(self):
        return f"{self.employee.name} - {self.month}/{self.year}"
