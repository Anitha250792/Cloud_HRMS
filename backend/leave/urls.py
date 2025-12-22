from rest_framework.routers import DefaultRouter
from .views import LeaveViewSet, my_leaves
from django.urls import path

router = DefaultRouter()
router.register("leave", LeaveViewSet, basename="leave")

urlpatterns = router.urls + [
    path("leave/my/", my_leaves),
]
