import os
import tempfile
from calendar import monthrange
from django.http import HttpResponse, FileResponse
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

# PDF generators
from .utils import generate_payroll_pdf, generate_bulk_payroll_pdf
from .payslip import generate_payslip_pdf


# =====================================================================
#                           PAYROLL VIEWSET
# =====================================================================
class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.all().order_by("-id")  # FIXED: generated_on removed
    serializer_class = PayrollSerializer

    # ---------------------------------------------------------
    # Generate payroll for a single employee
    # ---------------------------------------------------------
    @action(detail=False, methods=["post"])
    def generate_salary(self, request):
        employee_id = request.data.get("employee_id")
        month = int(request.data.get("month"))
        year = int(request.data.get("year"))

        if not employee_id:
            return Response({"error": "employee_id required"}, status=400)

        employee = Employee.objects.get(id=employee_id)
        working_days = monthrange(year, month)[1]

        attendance = Attendance.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        )

        present_days = attendance.count()
        absent_days = working_days - present_days

        per_day_salary = float(employee.salary) / working_days
        lop_amount = per_day_salary * absent_days

        gross_salary = float(employee.salary)
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
            gross_salary=gross_salary,
            net_salary=round(net_salary, 2),
        )

        return Response(PayrollSerializer(payroll).data, status=201)

    # ---------------------------------------------------------
    # Return payslip for one payroll entry (PDF)
    # ---------------------------------------------------------
    @action(detail=True, methods=["get"])
    def payslip(self, request, pk=None):
        payroll = self.get_object()
        return generate_payslip_pdf(payroll)


# =====================================================================
#          GENERATE PAYROLL FOR ALL EMPLOYEES (BUTTON PRESS)
# =====================================================================
@api_view(["POST"])
def generate_all_payroll(request):
    month = int(request.data.get("month", timezone.localdate().month))
    year = int(request.data.get("year", timezone.localdate().year))

    employees = Employee.objects.all()
    working_days = monthrange(year, month)[1]

    count = 0
    for emp in employees:
        attendance = Attendance.objects.filter(
            employee=emp,
            date__year=year,
            date__month=month
        )

        present_days = attendance.count()
        absent_days = working_days - present_days

        per_day_salary = float(emp.salary) / working_days
        lop_amount = per_day_salary * absent_days

        gross_salary = float(emp.salary)
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
                "net_salary": round(net_salary, 2),
            }
        )
        count += 1

    return Response({
        "message": f"Payroll generated for {count} employees",
        "month": month,
        "year": year
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
#                         CHART API
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
#                       PDF Download (single)
# =====================================================================
@api_view(["GET"])
def download_payroll_pdf(request, pk):
    payroll = Payroll.objects.get(id=pk)
    file_path = f"salary_slip_{pk}.pdf"

    generate_payroll_pdf(payroll, file_path)

    return FileResponse(open(file_path, "rb"), as_attachment=True)


# =====================================================================
#           EMPLOYEE PAYSLIP HISTORY (for frontend)
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
#                       BULK PDF DOWNLOAD
# =====================================================================
@api_view(["GET"])
def download_bulk_payroll_pdf(request):
    year = int(request.GET.get("year", timezone.localdate().year))
    month = int(request.GET.get("month", timezone.localdate().month))

    payrolls = Payroll.objects.filter(year=year, month=month)

    if not payrolls.exists():
        return Response({"error": "No payroll found"}, status=404)

    file_path = f"payroll_bulk_{year}_{month}.pdf"
    generate_bulk_payroll_pdf(payrolls, file_path, year, month)

    return FileResponse(open(file_path, "rb"), as_attachment=True)


# =====================================================================
#                       SEND PAYSLIP EMAIL
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


# =====================================================================
#                       GENERATE SINGLE PAYSLIP DOWNLOAD
# =====================================================================
def download_payslip(request, payroll_id):
    try:
        payroll = Payroll.objects.get(id=payroll_id)
    except Payroll.DoesNotExist:
        return HttpResponse("Payroll not found", status=404)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    file_path = temp.name

    generate_payroll_pdf(payroll, file_path)

    with open(file_path, "rb") as f:
        pdf_data = f.read()

    os.remove(file_path)

    response = HttpResponse(pdf_data, content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=payslip_{payroll_id}.pdf"

    return response
