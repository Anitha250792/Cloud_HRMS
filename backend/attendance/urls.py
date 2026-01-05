from django.urls import path
from .views import (
    AttendanceViewSet,
    my_today_attendance,
    attendance_summary_today,
    attendance_heatmap,
)

urlpatterns = [
    path("check-in/", AttendanceViewSet.as_view({"post": "check_in"})),
    path("check-out/", AttendanceViewSet.as_view({"post": "check_out"})),
    path("my-today/", my_today_attendance),

    path("summary/today/", attendance_summary_today),
    path("heatmap/<int:emp_id>/<int:year>/<int:month>/", attendance_heatmap),
]
