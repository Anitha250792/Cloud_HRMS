from django.urls import path
from .views import (
    check_in,
    check_out,
    my_today_attendance,
)

urlpatterns = [
    path("check-in/", check_in),
    path("check-out/", check_out),
    path("my-today/", my_today_attendance),
]
