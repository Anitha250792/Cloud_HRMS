from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import Attendance
from .serializers import AttendanceSerializer
from employees.models import Employee


# ------------------------------------------------------
# HELPER
# ------------------------------------------------------
def get_active_employee(user=None):
    return Employee.objects.first()


# ------------------------------------------------------
# ATTENDANCE VIEWSET
# ------------------------------------------------------
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by("-id")
    serializer_class = AttendanceSerializer

    # ---------------- CHECK-IN ----------------
    @action(methods=["post"], detail=False, url_path="check-in")
    def check_in(self, request):
        employee = Employee.objects.first()
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

        return Response({"message": "Check-in successful"})


    # ---------------- CHECK-OUT ----------------
    @action(methods=["post"], detail=False, url_path="check-out")
    def check_out(self, request):
        employee = Employee.objects.first()
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

        return Response({"message": "Check-out successful"})


# ------------------------------------------------------
# MY TODAY ATTENDANCE  (/attendance/my-today/)
# ------------------------------------------------------
@api_view(["GET"])
def my_today_attendance(request):

    employee = Employee.objects.first()

    if not employee:
        return Response({"status":"NO_EMPLOYEE"})

    today = timezone.localdate()

    record = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    if not record:
        return Response({
            "status":"NOT_MARKED"
        })

    return Response({
        "status":"PRESENT",
        "check_in": record.check_in,
        "check_out": record.check_out,
        "working_hours": record.working_hours,
        "is_checked_in": bool(
            record.check_in and
            not record.check_out
        ),
    })



# ------------------------------------------------------
# MY ATTENDANCE RECORDS  (/attendance/records/)
# ------------------------------------------------------


@api_view(["GET"])
def attendance_records(request):

    records = Attendance.objects.select_related(
        "employee"
    ).all().order_by("-date")

    serializer = AttendanceSerializer(
        records,
        many=True
    )

    return Response(serializer.data)


# ------------------------------------------------------
# ATTENDANCE BALANCE  (/attendance/balance/)
# ------------------------------------------------------


@api_view(["GET"])
def attendance_balance(request):

    total_days = Attendance.objects.count()

    present_days = Attendance.objects.filter(
        check_in__isnull=False
    ).count()

    absent_days = max(
        total_days - present_days,
        0
    )

    return Response({
        "total_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
    })



@api_view(["GET"])
def attendance_summary(request):

    total_days = Attendance.objects.count()

    worked_days = Attendance.objects.filter(
        check_out__isnull=False
    ).count()

    return Response({
        "total_days": total_days,
        "worked_days": worked_days,
    })
