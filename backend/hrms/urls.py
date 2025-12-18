from django.contrib import admin 
from django.urls import path, include
from .views import RoleRedirectView
from auth.views import google_login            # ✔ your google view
from employees.auth_api import RegisterAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", RoleRedirectView.as_view(), name="root"),

    # Django admin
    path("admin/", admin.site.urls),

    # AUTH ROUTES (local login + logout + refresh)
    path("api/auth/", include("auth.urls")),

    # Custom register with role
    path("api/auth/register/", RegisterAPIView.as_view(), name="custom-register"),

    # GOOGLE LOGIN — ✔ only ONE route
    path("api/auth/google/", google_login),

    # BUSINESS APIs
    path("api/employees/", include("employees.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/leave/", include("leave.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
