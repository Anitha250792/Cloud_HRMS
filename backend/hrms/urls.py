from django.contrib import admin 
from django.urls import path, include
from .views import RoleRedirectView, admin_dashboard_stats
from auth.views import google_login            # ✔ your google view
from employees.auth_api import RegisterAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
from django.views.generic import TemplateView    
)

urlpatterns = [
    path("", RoleRedirectView.as_view(), name="root"),

    # Django admin
    path("admin/", admin.site.urls),

    # AUTH
    path("api/auth/", include("auth.urls")),
    path("api/auth/register/", RegisterAPIView.as_view()),
    path("api/auth/google/", google_login),

    # BUSINESS APIs
    path("api/employees/", include("employees.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/leave/", include("leave.urls")),

    # JWT
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),

    # ✅ DASHBOARD STATS
    path("api/dashboard/stats/", admin_dashboard_stats),

    path("<path:path>", TemplateView.as_view(template_name="index.html")),
]
