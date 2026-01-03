from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LeaveViewSet, my_leaves, leave_balance

router = DefaultRouter()
router.register("", LeaveViewSet, basename="leave")

urlpatterns = router.urls + [
    path("", LeaveViewSet.as_view({"get": "list"})),
    path("apply/", LeaveViewSet.as_view({"post": "create"})),
    path("my/", my_leaves),
    path("balance/", leave_balance),
]
