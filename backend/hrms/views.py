# backend/hrms/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from employees.models import Employee
from leave.models import Leave
from payroll.models import Payroll
from django.utils import timezone


class RoleRedirectView(APIView):
    """
    Root URL responds with a simple JSON message.
    No authentication or permissions required.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "HRMS Backend Running"})

     @api_view(["GET"])
def admin_dashboard_stats(request):
    """
    Admin / HR dashboard summary
    """
    today = timezone.localdate()

    return Response({
        "total_employees": Employee.objects.filter(is_active=True).count(),
        "pending_leaves": Leave.objects.filter(status="PENDING").count(),
        "payroll_this_month": Payroll.objects.filter(
            month=today.month,
            year=today.year
        ).count(),
    })   
