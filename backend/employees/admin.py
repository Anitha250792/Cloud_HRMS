from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "emp_code",
        "name",
        "email",
        "department",
        "role",
        "salary",
        "date_joined",
        "is_active",
        "user",
    )

    search_fields = ("emp_code", "name", "email")
    list_filter = ("department", "role", "is_active")
    ordering = ("-id",)
    readonly_fields = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    @admin.action(description="Deactivate selected employees")
    def deactivate_employees(self, request, queryset):
        queryset.update(is_active=False)

    actions = ["deactivate_employees"]
