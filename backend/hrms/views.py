from django.utils import timezone
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from employees.models import Employee
from attendance.models import Attendance
from leave.models import Leave
from payroll.models import Payroll


class RoleRedirectView(APIView):
    """
    Root URL responds with a simple JSON message.
    No authentication required.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "HRMS Backend Running"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_dashboard_stats(request):
    today = timezone.localdate()

    total_employees = Employee.objects.filter(is_active=True).count()

    present_today = Attendance.objects.filter(
        date=today,
        check_in__isnull=False
    ).count()

    pending_leaves = Leave.objects.filter(status="PENDING").count()

    payroll_total = Payroll.objects.filter(
        month=today.month,
        year=today.year
    ).aggregate(
        total=Sum("net_salary_value")
    )["total"] or 0

    return Response({
        "total_employees": total_employees,
        "present_today": present_today,
        "pending_leaves": pending_leaves,
        "payroll_this_month": payroll_total,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Render health check endpoint
    """
    return Response({"status": "ok"})
