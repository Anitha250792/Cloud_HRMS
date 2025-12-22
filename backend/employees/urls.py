from django.urls import path
from .views import (
    list_employees,
    create_employee,
    update_employee,
    delete_employee,
)

urlpatterns = [
    path("", list_employees, name="list_employees"),
    path("create/", create_employee, name="create_employee"),
    path("update/<int:pk>/", update_employee, name="update_employee"),
    path("delete/<int:pk>/", delete_employee, name="delete_employee"),
]
