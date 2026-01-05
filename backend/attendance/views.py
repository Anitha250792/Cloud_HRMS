from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.utils import timezone
from datetime import date
from calendar import monthrange

from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceRecordSerializer
from employees.models import Employee


def get_active_employee(user):
    try:
        return Employee.objects.get(user=user, is_active=True)
    except Employee.DoesNotExist:
        return None


# ===================== CHECK-IN =====================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_in(request):
    employee = get_active_employee(request.user)
    if not employee:
        return Response({"error": "Employee not found"}, status=403)

    today = timezone.localdate()
    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today
    )

    if attendance.check_in:
        return Response({"error": "Already checked in"}, status=400)

    attendance.check_in = timezone.now()
    attendance.save()

    return Response({
        "message": "Check-in successful",
        "data": AttendanceSerializer(attendance).data
    })


# ===================== CHECK-OUT =====================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def check_out(request):
    employee = get_active_employee(request.user)
    if not employee:
        return Response({"error": "Employee not found"}, status=403)

    today = timezone.localdate()
    attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    if not attendance or not attendance.check_in:
        return Response({"error": "No check-in found"}, status=400)

    if attendance.check_out:
        return Response({"error": "Already checked out"}, status=400)

    attendance.check_out = timezone.now()

    diff = attendance.check_out - attendance.check_in
    attendance.working_hours = round(diff.total_seconds() / 3600, 2)

    attendance.save()

    return Response({
        "message": "Check-out successful",
        "working_hours": attendance.working_hours
    })


# ===================== EMPLOYEE DASHBOARD =====================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_today_attendance(request):
    employee = get_active_employee(request.user)
    if not employee:
        return Response({"status": "NO_EMPLOYEE"}, status=403)

    today = timezone.localdate()
    record = Attendance.objects.filter(employee=employee, date=today).first()

    if not record:
        return Response({
            "status": "NOT_MARKED",
            "check_in": None,
            "check_out": None,
            "working_hours": 0,
        })

    return Response({
        "status": "PRESENT",
        "check_in": record.check_in,
        "check_out": record.check_out,
        "working_hours": record.working_hours or 0,
    })
