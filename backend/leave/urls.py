from django.urls import path
from .views import apply_leave, my_leaves
from .views import LeaveViewSet

urlpatterns = [
    path("apply/", apply_leave),
    path("my/", my_leaves),

    # HR actions
    path("<int:pk>/approve/", LeaveViewSet.as_view({"post": "approve"})),
    path("<int:pk>/reject/", LeaveViewSet.as_view({"post": "reject"})),
]
