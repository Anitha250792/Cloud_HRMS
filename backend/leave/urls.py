from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LeaveViewSet, my_leaves

router = DefaultRouter()
router.register("", LeaveViewSet, basename="leave")

urlpatterns = [
    
    path("my/", my_leaves),
]
