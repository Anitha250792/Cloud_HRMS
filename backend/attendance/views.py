# attendance/views.py
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date
from calendar import monthrange

from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceRecordSerializer
from employees.models import Employee


# ==========================================================
# HELPER
# ==========================================================
def get_active_employee(user):
    try:
        return Employee.objects.get(user=user, is_active=True)
    except Employee.DoesNotExist:
        return None


# ==========================================================
# ATTENDANCE VIEWSET
# ==========================================================
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    # ---------------- CHECK-IN ----------------
    @action(methods=["post"], detail=False)
    def check_in(self, request):
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

    # ---------------- CHECK-OUT ----------------
    @action(methods=["post"], detail=False)
    def check_out(self, request):
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
        attendance.save()

        return Response({
            "message": "Check-out successful",
            "working_hours": attendance.working_hours
        })


# ==========================================================
# EMPLOYEE DASHBOARD API
# ==========================================================
@api_view(["GET"])
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
            "working_hours": 0
        })

    status_label = "PRESENT"
    if record.is_late:
        status_label = "LATE"
    if record.is_half_day:
        status_label = "HALF_DAY"

    return Response({
        "status": status_label,
        "check_in": record.check_in,
        "check_out": record.check_out,
        "working_hours": record.working_hours
    })


# ==========================================================
# HR APIs
# ==========================================================
@api_view(["GET"])
def attendance_summary_today(request):
    if request.user.role != "HR":
        return Response({"error": "Unauthorized"}, status=403)

    today = timezone.localdate()
    total = Employee.objects.filter(is_active=True).count()
    present = Attendance.objects.filter(date=today).count()

    return Response({
        "date": today,
        "total": total,
        "present": present,
        "absent": total - present
    })


@api_view(["GET"])
def attendance_heatmap(request, emp_id, year, month):
    if request.user.role != "HR":
        return Response({"error": "Unauthorized"}, status=403)

    employee = Employee.objects.get(id=emp_id)
    days = monthrange(year, month)[1]

    data = []
    for d in range(1, days + 1):
        current = date(year, month, d)
        record = Attendance.objects.filter(employee=employee, date=current).first()

        if not record:
            status = "ABSENT"
        elif record.is_half_day:
            status = "HALF_DAY"
        elif record.is_late:
            status = "LATE"
        else:
            status = "PRESENT"

        data.append({"date": current, "status": status})

    return Response(data)
