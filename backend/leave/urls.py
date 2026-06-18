from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    LeaveViewSet,
    my_leaves,
    leave_balance,
    approve_leave,
    reject_leave,
    pending_leaves,
)

router = DefaultRouter()
router.register("", LeaveViewSet, basename="leave")

urlpatterns = [
    path("my/", my_leaves),
    path("balance/", leave_balance),
    path("pending/", pending_leaves),
    path("<int:leave_id>/approve/", approve_leave),
    path("<int:leave_id>/reject/", reject_leave),
]

urlpatterns += router.urls