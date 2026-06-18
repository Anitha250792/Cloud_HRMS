from django.urls import path
from .views import (
    list_employees,
    create_employee,
    update_employee,
    delete_employee,
    get_employee,
)

urlpatterns = [
    path("", list_employees),
    path("create/", create_employee),
    path("<int:pk>/", get_employee),
    path("update/<int:pk>/", update_employee),
    path("delete/<int:pk>/", delete_employee),
]