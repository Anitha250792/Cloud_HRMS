from rest_framework.decorators import (
    api_view,
    permission_classes
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from employees.models import Employee
from leave.models import Leave
from payroll.models import Payroll

from django.utils import timezone


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):

    today = timezone.localdate()

    employees = Employee.objects.filter(
        is_active=True
    ).count()

    pending_leaves = Leave.objects.filter(
        status="PENDING"
    ).count()

    approved_leaves = Leave.objects.filter(
        status="APPROVED"
    ).count()

    rejected_leaves = Leave.objects.filter(
        status="REJECTED"
    ).count()

    generated_payslips = Payroll.objects.filter(
        month=today.month,
        year=today.year
    ).count()

    return Response({
        "employees": employees,
        "pending_leaves": pending_leaves,
        "approved_leaves": approved_leaves,
        "rejected_leaves": rejected_leaves,
        "generated_payslips": generated_payslips
    })