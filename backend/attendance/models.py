# attendance/models.py
from django.db import models
from django.utils import timezone
from datetime import time
from employees.models import Employee


class Attendance(models.Model):
    # ================= BASIC =================
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    date = models.DateField(default=timezone.localdate)

    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    # ================= CALCULATED =================
    working_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    # ================= STATUS FLAGS =================
    is_late = models.BooleanField(default=False)
    is_half_day = models.BooleanField(default=False)

    # ================= OFFICE TIME =================
    OFFICE_START = time(9, 0)   # 09:00 AM
    OFFICE_END = time(17, 0)    # 05:00 PM
    HALF_DAY_HOURS = 4          # < 4 hrs = half day

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        """
        Auto-calculate:
        - working hours
        - late login
        - half day
        """

        # ---------- CHECK LATE ----------
        if self.check_in:
            check_in_time = timezone.localtime(self.check_in).time()
            self.is_late = check_in_time > self.OFFICE_START

        # ---------- CALCULATE HOURS ----------
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            hours = round(delta.total_seconds() / 3600, 2)
            self.working_hours = hours

            # ---------- HALF DAY RULE ----------
            self.is_half_day = hours < self.HALF_DAY_HOURS
        else:
            self.working_hours = 0
            self.is_half_day = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} | {self.date} | {self.working_hours} hrs"
