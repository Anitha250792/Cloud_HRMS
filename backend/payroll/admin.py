from django.contrib import admin
from .models import Payroll

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = (
        "employee", "month", "year",
        "basic_salary", "present_days",
        "absent_days", "net_salary",
        "generated_on",
    )
    list_filter = ("year", "month", "employee")
    search_fields = ("employee__name",)
