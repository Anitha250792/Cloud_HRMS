from django.urls import path
from . import views   # ✅ IMPORTANT

urlpatterns = [
    path("", views.list_employees),
    path("create/", views.create_employee),
    path("<int:pk>/", views.get_employee),
    path("update/<int:pk>/", views.update_employee),
    path("delete/<int:pk>/", views.delete_employee),
]
