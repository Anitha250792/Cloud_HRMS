from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import LeaveViewSet, my_leaves

router = DefaultRouter()
router.register("", LeaveViewSet, basename="leave")

urlpatterns = router.urls + [
    path("apply/", LeaveViewSet.as_view({"post": "apply"})),
    path("<int:pk>/approve/", LeaveViewSet.as_view({"post": "approve"})),
    path("<int:pk>/reject/", LeaveViewSet.as_view({"post": "reject"})),
    path("my/<str:emp_code>/", my_leaves),
]
