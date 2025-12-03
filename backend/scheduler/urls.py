from django.urls import path
from .views import run_payroll_scheduler

urlpatterns = [
    path("run/", run_payroll_scheduler),
]
