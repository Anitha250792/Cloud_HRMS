from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from django.utils import timezone

from employees.models import Employee
from leave.models import Leave
from payroll.models import Payroll
from django.http import JsonResponse


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

def health_check(request):
    return JsonResponse({"status": "ok"})    
