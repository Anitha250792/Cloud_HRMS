from django.http import JsonResponse
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from employees.models import Employee
from leave.models import Leave
from payroll.models import Payroll


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
@permission_classes([AllowAny])
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


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Render health check endpoint
    """
    return Response({"status": "ok"})
