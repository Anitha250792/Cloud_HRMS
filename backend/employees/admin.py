from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("emp_code", "name", "email", "department", "role", "salary", "date_joined")
    search_fields = ("name", "email", "emp_code")
