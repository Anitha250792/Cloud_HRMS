from django.urls import path
from .views import (
    list_employees,
    create_employee,
    delete_employee,
    update_employee,
)

urlpatterns = [
    path("", list_employees),
    path("create/", create_employee),
    path("<int:pk>/", views.get_employee),  
    path("update/<int:pk>/", update_employee),   # ✅ ADD THIS
    path("delete/<int:pk>/", delete_employee),
]
