from django.contrib import admin
from .models import Payroll

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "month",
        "year",
        "basic_salary",
        "working_days",
        "present_days",
        "gross_salary",
        "net_salary",
    )
    list_filter = ("year", "month", "employee")
    search_fields = ("employee__name",)
