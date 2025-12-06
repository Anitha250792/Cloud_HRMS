from django.urls import path
from .views_pdf import download_payslip
from . import views

urlpatterns = [
    path("summary/", views.payroll_summary),
    path("stats/", views.payroll_chart),

    path("download/<int:payroll_id>/", download_payslip),
    path("bulk_download/", views.download_bulk_payroll_pdf),

    path("employee/<int:employee_id>/", views.employee_payslips),
    path("email/<int:pk>/", views.email_payslip),

    path("generate-all/", views.generate_all_payroll),   # POST-only
]
