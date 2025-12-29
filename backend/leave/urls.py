from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LeaveViewSet, my_leaves, leave_balance

router = DefaultRouter()
router.register("", LeaveViewSet, basename="leave")

urlpatterns = router.urls + [
    path("my/", my_leaves),
    path("balance/", leave_balance),
]
