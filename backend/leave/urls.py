from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LeaveViewSet, my_leaves

router = DefaultRouter()
router.register("", LeaveViewSet, basename="leave")

urlpatterns = [
    path("apply/", LeaveViewSet.as_view({"post": "apply"})),
    path("my/", my_leaves),
    path("<int:pk>/approve/", LeaveViewSet.as_view({"post": "approve"})),
    path("<int:pk>/reject/", LeaveViewSet.as_view({"post": "reject"})),
]
