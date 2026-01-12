from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from .views import RoleRedirectView, admin_dashboard_stats, health_check
from accounts.views import RegisterView, LoginView

urlpatterns = [
    # Health
    path("health/", health_check),

    # Root
    path("", RoleRedirectView.as_view(), name="root"),

    # Admin
    path("admin/", admin.site.urls),

    # ✅ AUTH (ONLY CUSTOM)
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", LoginView.as_view()),

    # Business APIs
    path("api/employees/", include("employees.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/leave/", include("leave.urls")),

    # Dashboard
    path("api/dashboard/stats/", admin_dashboard_stats),

    # Frontend SPA
    path("<path:path>", TemplateView.as_view(template_name="index.html")),
]
