from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LeaveViewSet, leave_type_distribution, leave_monthly_trend

router = DefaultRouter()
router.register("", LeaveViewSet, basename="leaves")

urlpatterns = []

# Base CRUD routes
urlpatterns += router.urls

# Actions
urlpatterns += [
    path("apply/", LeaveViewSet.as_view({"post": "apply"})),
    path("<int:pk>/approve/", LeaveViewSet.as_view({"post": "approve"})),
    path("<int:pk>/reject/", LeaveViewSet.as_view({"post": "reject"})),
]

# Analytics
urlpatterns += [
    path("analytics/type/", leave_type_distribution),
    path("analytics/monthly/", leave_monthly_trend),
]
