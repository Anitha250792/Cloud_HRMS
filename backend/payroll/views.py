import os
from calendar import monthrange
from django.http import FileResponse
from django.core.mail import EmailMessage
from django.utils import timezone
from django.db.models import Sum

from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Payroll
from .serializers import PayrollSerializer
from employees.models import Employee
from attendance.models import Attendance

from .utils import (
    generate_payroll_pdf,
    generate_bulk_payroll_pdf
)
from .payslip import generate_payslip_pdf


# =====================================================================
#                         VIEWSET FOR NORMAL CRUD
# =====================================================================

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all().order_by("-generated_on")
    serializer_class = PayrollSerializer

    # ---------------------------------------------------------
    # Generate payroll for a single employee
    # ---------------------------------------------------------
    @action(detail=False, methods=["post"])
    def generate_salary(self, request):
        employee_id = request.data.get("employee_id")
        month = int(request.data.get("month"))
        year = int(request.data.get("year"))

        employee = Employee.objects.get(id=employee_id)
        working_days = monthrange(year, month)[1]

        attendance = Attendance.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        )

        present_days = attendance.count()
        absent_days = working_days - present_days

        per_day_salary = employee.salary / working_days
        lop_amount = per_day_salary * absent_days

        gross_salary = employee.salary
        net_salary = gross_salary - lop_amount

        payroll = Payroll.objects.create(
            employee=employee,
            month=month,
            year=year,
            basic_salary=employee.salary,
            working_days=working_days,
            present_days=present_days,
            absent_days=absent_days,
            lop_days=absent_days,
            overtime_pay=0,
            gross_salary=gross_salary,
            net_salary=net_salary,
        )

        return Response(PayrollSerializer(payroll).data, status=201)

    # ---------------------------------------------------------
    # Payslip PDF for one payroll entry
    # ---------------------------------------------------------
    @action(detail=True, methods=["get"])
    def payslip(self, request, pk=None):
        payroll = self.get_object()
        return generate_payslip_pdf(payroll)


# =====================================================================
#                   MANUAL (BUTTON) — GENERATE ALL PAYROLL
# =====================================================================
@api_view(["POST"])
def generate_all_payroll(request):
    month = request.data.get("month", timezone.localdate().month)
    year = request.data.get("year", timezone.localdate().year)

    employees = Employee.objects.all()
    working_days = monthrange(int(year), int(month))[1]

    count = 0
    for emp in employees:

        attendance = Attendance.objects.filter(
            employee=emp,
            date__year=year,
            date__month=month
        )

        present_days = attendance.count()
        absent_days = working_days - present_days

        per_day_salary = emp.salary / working_days
        lop_amount = per_day_salary * absent_days

        gross_salary = emp.salary
        net_salary = gross_salary - lop_amount

        Payroll.objects.update_or_create(
            employee=emp,
            month=month,
            year=year,
            defaults={
                "basic_salary": emp.salary,
                "working_days": working_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "lop_days": absent_days,
                "gross_salary": gross_salary,
                "net_salary": net_salary,
            }
        )
        count += 1

    return Response({
        "message": f"Payroll generated for {count} employees",
        "month": month,
        "year": year
    }, status=200)


# =====================================================================
#                   CELERY — AUTOMATED MONTHLY PAYROLL
# =====================================================================
@api_view(["POST"])
def generate_all_payroll_async(request):
    month = request.data.get("month")
    year = request.data.get("year")

    if not month or not year:
        return Response({"error": "month and year required"}, status=400)

    from .tasks import generate_monthly_payroll
    generate_monthly_payroll.delay(int(year), int(month))

    return Response({"message": "Payroll generation started (Celery)"}, status=200)


# =====================================================================
#                     API: SUMMARY FOR DASHBOARD
# =====================================================================
@api_view(["GET"])
def payroll_summary(request):
    year = int(request.GET.get("year", timezone.localdate().year))
    month = int(request.GET.get("month", timezone.localdate().month))

    payroll = Payroll.objects.filter(year=year, month=month)

    return Response({
        "year": year,
        "month": month,
        "salary_generated_for": payroll.count(),
        "total_gross_salary": payroll.aggregate(Sum("gross_salary"))["gross_salary__sum"] or 0,
        "total_net_salary": payroll.aggregate(Sum("net_salary"))["net_salary__sum"] or 0,
    })


# =====================================================================
#              API: CHART DATA (MONTHLY GROSS vs NET)
# =====================================================================
@api_view(["GET"])
def payroll_chart(request):
    year = int(request.GET.get("year", timezone.localdate().year))

    data = Payroll.objects.filter(year=year).values("month").annotate(
        total_gross_salary=Sum("gross_salary"),
        total_net_salary=Sum("net_salary")
    ).order_by("month")

    return Response(list(data))


# =====================================================================
#                   PDF DOWNLOAD (single)
# =====================================================================
@api_view(["GET"])
def download_payroll_pdf(request, pk):
    payroll = Payroll.objects.get(id=pk)
    file_path = f"salary_slip_{pk}.pdf"
    generate_payroll_pdf(payroll, file_path)
    return FileResponse(open(file_path, "rb"), as_attachment=True)


# =====================================================================
#                   EMPLOYEE PAYSLIP HISTORY
# =====================================================================
@api_view(["GET"])
def employee_payslips(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    queryset = Payroll.objects.filter(employee=employee).order_by("-year", "-month")

    return Response({
        "employee": employee.name,
        "employee_id": employee.id,
        "payslips": PayrollSerializer(queryset, many=True).data,
    })


# =====================================================================
#                     BULK PDF (all payslips)
# =====================================================================
@api_view(["GET"])
def download_bulk_payroll_pdf(request):
    year = int(request.GET.get("year", timezone.localdate().year))
    month = int(request.GET.get("month", timezone.localdate().month))

    payrolls = Payroll.objects.filter(year=year, month=month).select_related("employee")

    if not payrolls.exists():
        return Response({"error": "No payroll found"}, status=404)

    file_path = f"payroll_bulk_{year}_{month}.pdf"
    generate_bulk_payroll_pdf(payrolls, file_path, year, month)

    return FileResponse(open(file_path, "rb"), as_attachment=True)


# =====================================================================
#                     SEND PAYSLIP VIA EMAIL
# =====================================================================
@api_view(["POST"])
def email_payslip(request, pk):
    payroll = Payroll.objects.get(id=pk)

    tmp = f"salary_slip_{pk}.pdf"
    generate_payroll_pdf(payroll, tmp)

    email = EmailMessage(
        subject=f"Salary Slip {payroll.month}/{payroll.year}",
        body=f"Dear {payroll.employee.name}, your payslip is attached.",
        to=[payroll.employee.email],
    )

    email.attach_file(tmp)
    email.send()

    return Response({"message": "Payslip sent successfully"})
