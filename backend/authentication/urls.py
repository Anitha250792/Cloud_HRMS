from django.urls import path
from dj_rest_auth.views import LoginView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

from .views import register_user, login_user

urlpatterns = [
    # ===============================
    # CUSTOM AUTH (UNCHANGED)
    # ===============================
    path("register/", register_user, name="custom-register"),
    path("login/", login_user, name="custom-login"),

    # ===============================
    # DJ-REST-AUTH (JWT BASED)
    # ===============================
    path("login/jwt/", LoginView.as_view(), name="jwt-login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # ===============================
    # JWT REFRESH
    # ===============================
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
