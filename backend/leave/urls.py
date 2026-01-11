from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LeaveViewSet, my_leaves, leave_balance, apply_leave, pending_leaves

router = DefaultRouter()
router.register("", LeaveViewSet, basename="leave")

urlpatterns = [
    path("my/", my_leaves),
    path("balance/", leave_balance),
    path("apply/", apply_leave),
    path("pending/", pending_leaves),
]
