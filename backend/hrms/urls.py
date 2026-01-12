from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    RoleRedirectView,
    admin_dashboard_stats,
    health_check,
)

from accounts.views import RegisterView, LoginView

urlpatterns = [
    # ========================
    # HEALTH CHECK
    # ========================
    path("health/", health_check),

    # ========================
    # ROOT
    # ========================
    path("", RoleRedirectView.as_view(), name="root"),

    # ========================
    # ADMIN
    # ========================
    path("admin/", admin.site.urls),

    # ========================
    # AUTH (JWT + CUSTOM)
    # ========================
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ========================
    # BUSINESS APIs
    # ========================
    path("api/employees/", include("employees.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/leave/", include("leave.urls")),

    # ========================
    # DASHBOARD
    # ========================
    path("api/dashboard/stats/", admin_dashboard_stats),

    # ========================
    # FRONTEND (SPA)
    # ========================
    path("<path:path>", TemplateView.as_view(template_name="index.html")),
]
