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


def get_active_employee(user):
    return Employee.objects.filter(user=user, is_active=True).first()


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by("-id")
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=["post"], detail=False, url_path="check-in")
    def check_in(self, request):
        employee = get_active_employee(request.user)
        if not employee:
            return Response({"error": "Employee not found"}, status=403)

        today = timezone.localdate()
        attendance, _ = Attendance.objects.get_or_create(
            employee=employee, date=today
        )

        if attendance.check_in:
            return Response({"error": "Already checked in"}, status=400)

        attendance.check_in = timezone.now()
        attendance.save()
        return Response({"message": "Check-in successful"})

    @action(methods=["post"], detail=False, url_path="check-out")
    def check_out(self, request):
        employee = get_active_employee(request.user)
        if not employee:
            return Response({"error": "Employee not found"}, status=403)

        today = timezone.localdate()
        attendance = Attendance.objects.filter(
            employee=employee, date=today
        ).first()

        if not attendance or not attendance.check_in:
            return Response({"error": "No check-in found"}, status=400)

        if attendance.check_out:
            return Response({"error": "Already checked out"}, status=400)

        attendance.check_out = timezone.now()
        attendance.save()
        return Response({"message": "Check-out successful"})


@api_view(["GET"])
def my_today_attendance(request):
    employee = get_active_employee(request.user)
    if not employee:
        return Response({"status": "NO_EMPLOYEE"}, status=403)

    today = timezone.localdate()
    record = Attendance.objects.filter(employee=employee, date=today).first()

    if not record:
        return Response({"status": "NOT_MARKED"})

    status_label = "PRESENT"
    if record.check_in and not record.check_out and record.check_in.hour >= 9:
        status_label = "LATE"

    return Response({
        "status": status_label,
        "check_in": record.check_in,
        "check_out": record.check_out,
        "working_hours": record.working_hours,
    })
