from django.db import models
from employees.models import Employee


class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    month = models.IntegerField()
    year = models.IntegerField()

    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    working_days = models.IntegerField(default=30)
    present_days = models.IntegerField(default=0)

    gross_salary = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    net_salary_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    class Meta:
        unique_together = ("employee", "month", "year")
        ordering = ["-year", "-month"]

    def save(self, *args, **kwargs):
        """
        Auto-calculate salaries before saving
        """
        # Gross salary
        self.gross_salary = self.basic_salary

        # Salary per day
        per_day = float(self.basic_salary) / self.working_days

        # Loss of pay days
        lop_days = max(self.working_days - int(self.present_days), 0)

        # Net salary
        net = float(self.basic_salary) - (per_day * lop_days)
        self.net_salary_value = round(net, 2)

        super().save(*args, **kwargs)

    @property
    def net_salary(self):
        """
        Expose net salary cleanly for serializer & frontend
        """
        return float(self.net_salary_value)

    def __str__(self):
        return f"{self.employee.name} - {self.month}/{self.year}"
