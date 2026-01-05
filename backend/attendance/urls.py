from django.urls import path
from .views import AttendanceViewSet, my_today_attendance

urlpatterns = [
    path("check-in/", AttendanceViewSet.as_view({"post": "check_in"})),
    path("check-out/", AttendanceViewSet.as_view({"post": "check_out"})),
    path("my-today/", my_today_attendance),
]
