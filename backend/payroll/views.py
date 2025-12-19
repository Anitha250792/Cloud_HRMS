import os
import tempfile
from calendar import monthrange

from django.http import HttpResponse, FileResponse
from django.core.mail import EmailMessage
from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Payroll
from .serializers import PayrollSerializer
from employees.models import Employee
from attendance.models import Attendance

# PDF generators
from .utils import generate_payroll_pdf, generate_bulk_payroll_pdf
from .payslip import generate_payslip_pdf


# =====================================================================
#                           PAYROLL VIEWSET
# =====================================================================
class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all().order_by("-year", "-month", "-id")
    serializer_class = PayrollSerializer

    # ---------------------------------------------------------
    # Generate payroll for a SINGLE employee
    # ---------------------------------------------------------
    @action(detail=False, methods=["post"])
    def generate_salary(self, request):
        employee_id = request.data.get("employee_id")
        month = request.data.get("month")
        year = request.data.get("year")

        if not employee_id or not month or not year:
            return Response(
                {"error": "employee_id, month and year are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee = get_object_or_404(Employee, id=employee_id)
        month, year = int(month), int(year)

        # Prevent duplicate payroll
        if Payroll.objects.filter(employee=employee, month=month, year=year).exists():
            return Response(
                {"error": "Payroll already generated for this employee"},
                status=status.HTTP_409_CONFLICT
            )

        working_days = monthrange(year, month)[1]

        attendance_qs = Attendance.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        )

        present_days = attendance_qs.count()
        absent_days = max(working_days - present_days, 0)

        per_day_salary = float(employee.salary) / working_days
        lop_amount = per_day_salary * absent_days

        gross_salary = float(employee.salary)
        net_salary = round(gross_salary - lop_amount, 2)

        payroll = Payroll.objects.create(
            employee=employee,
            month=month,
            year=year,
            basic_salary=employee.salary,
            working_days=working_days,
            present_days=present_days,
            absent_days=absent_days,
            lop_days=absent_days,
            gross_salary=gross_salary,
            net_salary=net_salary,
        )

        return Response(
            PayrollSerializer(payroll).data,
            status=status.HTTP_201_CREATED
        )

    # ---------------------------------------------------------
    # Return payslip PDF
    # ---------------------------------------------------------
    @action(detail=True, methods=["get"])
    def payslip(self, request, pk=None):
        payroll = self.get_object()
        return generate_payslip_pdf(payroll)


# =====================================================================
#                       PAYROLL LIST API
# =====================================================================
@api_view(["GET"])
def payroll_list(request):
    payrolls = Payroll.objects.all().order_by("-year", "-month")
    return Response(PayrollSerializer(payrolls, many=True).data)


# =====================================================================
#               GENERATE PAYROLL FOR ALL EMPLOYEES
# =====================================================================
@api_view(["POST"])
def generate_all_payroll(request):
    if request.user.role != "HR":
        return Response(
            {"error": "Only HR can generate payroll"},
            status=403
        )

    try:
        month = int(request.data.get("month"))
        year = int(request.data.get("year"))
    except (TypeError, ValueError):
        return Response({"error": "Month and year required"}, status=400)

    working_days = monthrange(year, month)[1]
    employees = Employee.objects.filter(is_active=True)

    generated = 0

    for emp in employees:
        if not emp.salary or emp.salary <= 0:
            continue

        attendance_qs = Attendance.objects.filter(
            employee=emp,
            date__year=year,
            date__month=month
        )

        present_days = attendance_qs.count()
        absent_days = max(working_days - present_days, 0)
        per_day_salary = float(emp.salary) / working_days
        lop_amount = per_day_salary * absent_days

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
                "gross_salary": emp.salary,
                "net_salary": round(emp.salary - lop_amount, 2),
            }
        )

        generated += 1

    return Response({
        "message": "Payroll generated successfully",
        "employees_processed": generated,
        "month": month,
        "year": year,
    }, status=200)


# =====================================================================
#                       DASHBOARD SUMMARY API
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
#                             CHART API
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
#                       PDF DOWNLOAD (single)
# =====================================================================
@api_view(["GET"])
def download_payroll_pdf(request, pk):
    payroll = get_object_or_404(Payroll, id=pk)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    generate_payroll_pdf(payroll, temp.name)

    return FileResponse(open(temp.name, "rb"), as_attachment=True)


# =====================================================================
#                    EMPLOYEE PAYSLIP HISTORY
# =====================================================================
@api_view(["GET"])
def employee_payslips(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    payrolls = Payroll.objects.filter(employee=employee).order_by("-year", "-month")

    return Response({
        "employee": employee.name,
        "employee_id": employee.id,
        "payslips": PayrollSerializer(payrolls, many=True).data,
    })


# =====================================================================
#                      BULK PDF DOWNLOAD
# =====================================================================
@api_view(["GET"])
def download_bulk_payroll_pdf(request):
    year = int(request.GET.get("year", timezone.localdate().year))
    month = int(request.GET.get("month", timezone.localdate().month))

    payrolls = Payroll.objects.filter(year=year, month=month)

    if not payrolls.exists():
        return Response({"error": "No payroll found"}, status=404)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    generate_bulk_payroll_pdf(payrolls, temp.name, year, month)

    return FileResponse(open(temp.name, "rb"), as_attachment=True)


# =====================================================================
#                       SEND PAYSLIP EMAIL
# =====================================================================
@api_view(["POST"])
def email_payslip(request, pk):
    payroll = get_object_or_404(Payroll, id=pk)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    generate_payroll_pdf(payroll, temp.name)

    email = EmailMessage(
        subject=f"Salary Slip {payroll.month}/{payroll.year}",
        body=f"Dear {payroll.employee.name}, your payslip is attached.",
        to=[payroll.employee.email],
    )
    email.attach_file(temp.name)
    email.send()

    return Response({"message": "Payslip sent successfully"})


# =====================================================================
#                  DIRECT PAYSLIP DOWNLOAD (fallback)
# =====================================================================
def download_payslip(request, payroll_id):
    payroll = get_object_or_404(Payroll, id=payroll_id)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    generate_payroll_pdf(payroll, temp.name)

    with open(temp.name, "rb") as f:
        pdf_data = f.read()

    os.remove(temp.name)

    response = HttpResponse(pdf_data, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=payslip_{payroll_id}.pdf"
    return response


@api_view(["GET"])
def my_payrolls(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return Response([], status=200)

    payrolls = Payroll.objects.filter(employee=employee).order_by("-year", "-month")
    serializer = PayrollSerializer(payrolls, many=True)
    return Response(serializer.data)

