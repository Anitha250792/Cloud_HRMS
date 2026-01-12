from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from .views import (
    RoleRedirectView,
    admin_dashboard_stats,
    health_check,
)

from accounts.views import RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # ------------------------
    # HEALTH CHECK
    # ------------------------
    path("health/", health_check),

    # ------------------------
    # ROOT
    # ------------------------
    path("", RoleRedirectView.as_view(), name="root"),

    # ------------------------
    # ADMIN
    # ------------------------
    path("admin/", admin.site.urls),

    # ------------------------
    # AUTH (✅ ONLY THIS)
    # ------------------------
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", TokenObtainPairView.as_view()),
    path("api/auth/token/refresh/", TokenRefreshView.as_view()),

    # ------------------------
    # BUSINESS APIs
    # ------------------------
    path("api/employees/", include("employees.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/leave/", include("leave.urls")),

    # ------------------------
    # DASHBOARD
    # ------------------------
    path("api/dashboard/stats/", admin_dashboard_stats),

    # ------------------------
    # FRONTEND SPA
    # ------------------------
    path("<path:path>", TemplateView.as_view(template_name="index.html")),
]
