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


@@api_view(["GET"])
@permission_classes([AllowAny])
def admin_dashboard_stats(request):
    today = timezone.localdate()

    data = {
        "total_employees": 0,
        "present_today": 0,
        "pending_leaves": 0,
        "payroll_this_month": 0,
    }

    try:
        data["total_employees"] = Employee.objects.count()
    except Exception as e:
        print("EMPLOYEE ERROR:", e)

    try:
        data["present_today"] = Attendance.objects.filter(
            date=today
        ).count()
    except Exception as e:
        print("ATTENDANCE ERROR:", e)

    try:
        data["pending_leaves"] = Leave.objects.count()
    except Exception as e:
        print("LEAVE ERROR:", e)

    try:
        payroll = Payroll.objects.aggregate(
            total=Sum("net_salary")
        )["total"]
        data["payroll_this_month"] = payroll or 0
    except Exception as e:
        print("PAYROLL ERROR:", e)

    return Response(data)



@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Render health check endpoint
    """
    return Response({"status": "ok"})
