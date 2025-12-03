from django.urls import path
from .views import (
    attendance_summary_today,
    attendance_summary_month,
    attendance_heatmap,
    realtime_checkins
)

urlpatterns = [
    path("summary_today/", attendance_summary_today),
    path("summary_month/", attendance_summary_month),
    path("heatmap/<int:emp_id>/<int:year>/<int:month>/", attendance_heatmap),
    path("tools/realtime/", realtime_checkins),
]
