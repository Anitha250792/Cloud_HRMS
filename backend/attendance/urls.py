from django.urls import path
from .views import (
    AttendanceViewSet,
    attendance_summary_today,
    attendance_heatmap,
    realtime_checkins,
    attendance_records,
    my_today_attendance,
)

urlpatterns = [
    # Employee actions
    path("check-in/", AttendanceViewSet.as_view({"post": "check_in"})),
    path("check-out/", AttendanceViewSet.as_view({"post": "check_out"})),
    path("my-today/", my_today_attendance),

    # HR / Dashboard
    path("summary/today/", attendance_summary_today),
    path("daily-logs/", AttendanceViewSet.as_view({"get": "daily_logs"})),
    path("summary/month/", AttendanceViewSet.as_view({"get": "summary_month"})),
    path("records/", attendance_records),

    # Extras
    path("heatmap/<int:emp_id>/<int:year>/<int:month>/", attendance_heatmap),
    path("realtime/", realtime_checkins),
]
