from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from .views import (
    RoleRedirectView,
    admin_dashboard_stats,
    health_check,
)

from auth.views import google_login
from employees.auth_api import RegisterAPIView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # ✅ Render health check (MUST be first)
    path("health/", health_check),

    # Root
    path("", RoleRedirectView.as_view(), name="root"),

    # Django admin
    path("admin/", admin.site.urls),

    # AUTH
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/register/", include("dj_rest_auth.registration.urls")),
    path("api/auth/google/", google_login),
    path("api/auth/", include("dj_rest_auth.urls")),

    # BUSINESS APIs
    path("api/employees/", include("employees.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/leave/", include("leave.urls")),

    # JWT
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),

    # DASHBOARD
    path("api/dashboard/stats/", admin_dashboard_stats),

    # Frontend SPA catch-all
    path("<path:path>", TemplateView.as_view(template_name="index.html")),
]