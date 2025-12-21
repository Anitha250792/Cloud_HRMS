from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # ================= LIST VIEW =================
    list_display = (
        "emp_code",
        "name",
        "email",
        "department",
        "role",
        "salary",
        "date_joined",
        "is_active",
    )

    # ================= SEARCH =================
    search_fields = (
        "emp_code",
        "name",
        "email",
    )

    # ================= FILTERS =================
    list_filter = (
        "department",
        "role",
        "is_active",
    )

    # ================= DEFAULT ORDER =================
    ordering = ("-date_joined",)

    # ================= READ-ONLY FIELDS =================
    readonly_fields = ("date_joined",)

    # ================= SOFT DELETE AWARE =================
    def get_queryset(self, request):
        """
        Show only ACTIVE employees in admin by default
        (matches API behavior)
        """
        qs = super().get_queryset(request)
        return qs.filter(is_active=True)

    # ================= ADMIN ACTION =================
    @admin.action(description="Deactivate selected employees")
    def deactivate_employees(self, request, queryset):
        queryset.update(is_active=False)

    actions = ["deactivate_employees"]
