from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date
from calendar import monthrange

from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceRecordSerializer
from employees.models import Employee


# ==========================================================
# HELPER (SAFE EMPLOYEE FETCH)
# ==========================================================
def get_active_employee(user):
    try:
        return Employee.objects.get(user=user, is_active=True)
    except Employee.DoesNotExist:
        return None


# ==========================================================
# ATTENDANCE VIEWSET (EMPLOYEE + HR)
# ==========================================================
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by("-id")
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    # ---------------- CHECK-IN ----------------
@action(methods=["post"], detail=False)
def check_in(self, request):
    employee = get_active_employee(request.user)
    if not employee:
        return Response(
            {"error": "Employee profile not found or inactive. Contact HR."},
            status=403
        )

    today = timezone.localdate()

    attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    if attendance and attendance.check_in:
        return Response(
            {"error": "Already checked in today"},
            status=400
        )

    if not attendance:
        attendance = Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now()
        )
    else:
        attendance.check_in = timezone.now()
        attendance.save()

    return Response(
        {
            "message": "Check-in successful",
            "data": AttendanceSerializer(attendance).data,
        }
    )

    # ---------------- CHECK-OUT ----------------
@action(methods=["post"], detail=False)
def check_out(self, request):
    employee = get_active_employee(request.user)
    if not employee:
        return Response(
            {"error": "Employee profile not found or inactive. Contact HR."},
            status=403
        )

    today = timezone.localdate()

    attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    if not attendance:
        return Response(
            {"error": "You have not checked in today"},
            status=400
        )

    if attendance.check_out:
        return Response(
            {"error": "Already checked out today"},
            status=400
        )

    attendance.check_out = timezone.now()
    attendance.save()

    return Response(
        {
            "message": "Check-out successful",
            "data": AttendanceSerializer(attendance).data,
        }
    )



    # ---------------- HR DAILY LOGS ----------------
    @action(detail=False, methods=["get"])
    def daily_logs(self, request):
        if request.user.role != "HR":
            return Response({"error": "Unauthorized"}, status=403)

        date_filter = request.GET.get("date", timezone.localdate())
        logs = Attendance.objects.filter(date=date_filter)

        serializer = AttendanceRecordSerializer(logs, many=True)
        return Response(serializer.data)

    # ---------------- HR MONTH SUMMARY ----------------
    @action(detail=False, methods=["get"])
    def summary_month(self, request):
        if request.user.role != "HR":
            return Response({"error": "Unauthorized"}, status=403)

        month = int(request.GET.get("month", timezone.localdate().month))
        year = int(request.GET.get("year", timezone.localdate().year))

        records = Attendance.objects.filter(
            date__year=year,
            date__month=month
        )

        total_hours = sum(float(r.working_hours) for r in records)
        present_days = records.values("employee", "date").distinct().count()

        return Response(
            {
                "year": year,
                "month": month,
                "present_days": present_days,
                "total_hours_worked": round(total_hours, 2),
            }
        )


# ==========================================================
# EMPLOYEE DASHBOARD API
# ==========================================================
@api_view(["GET"])
def my_today_attendance(request):
    if not request.user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=401)

    employee = get_active_employee(request.user)
    if not employee:
        return Response(
            {
                "status": "NO_EMPLOYEE",
                "check_in": None,
                "check_out": None,
                "working_hours": 0,
            },
            status=403
        )

    today = timezone.localdate()
    record = Attendance.objects.filter(employee=employee, date=today).first()

    if not record:
        return Response(
            {
                "status": "NOT_MARKED",
                "check_in": None,
                "check_out": None,
                "working_hours": 0,
            }
        )

    status_label = "PRESENT"
    if record.check_in and not record.check_out and record.check_in.hour > 10:
        status_label = "LATE"

    return Response(
        {
            "status": status_label,
            "check_in": record.check_in,
            "check_out": record.check_out,
            "working_hours": record.working_hours or 0,
        }
    )

# ==========================================================
# HR DASHBOARD APIs
# ==========================================================
@api_view(["GET"])
def attendance_summary_today(request):
    if request.user.role != "HR":
        return Response({"error": "Unauthorized"}, status=403)

    today = timezone.localdate()
    total = Employee.objects.filter(is_active=True).count()
    present = Attendance.objects.filter(date=today).values("employee").distinct().count()

    return Response(
        {
            "date": today,
            "total_employees": total,
            "present_employees": present,
            "absent_employees": total - present,
        }
    )


@api_view(["GET"])
def attendance_heatmap(request, emp_id, year, month):
    if request.user.role != "HR":
        return Response({"error": "Unauthorized"}, status=403)

    try:
        employee = Employee.objects.get(id=emp_id, is_active=True)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    days = monthrange(year, month)[1]
    heatmap = []

    for d in range(1, days + 1):
        current = date(year, month, d)
        record = Attendance.objects.filter(employee=employee, date=current).first()

        if not record:
            status_label = "ABSENT"
        elif record.check_in and not record.check_out:
            status_label = "HALF_DAY"
        else:
            status_label = "PRESENT"

        heatmap.append({"date": current, "status": status_label})

    return Response(heatmap)


@api_view(["GET"])
def realtime_checkins(request):
    if request.user.role != "HR":
        return Response({"error": "Unauthorized"}, status=403)

    latest = Attendance.objects.select_related("employee").order_by("-check_in")[:10]

    return Response(
        [
            {
                "employee": att.employee.name,
                "check_in": att.check_in,
                "check_out": att.check_out,
                "working_hours": att.working_hours,
            }
            for att in latest
        ]
    )


@api_view(["GET"])
def attendance_records(request):
    if request.user.role != "HR":
        return Response({"error": "Unauthorized"}, status=403)

    records = Attendance.objects.select_related("employee").order_by("-date", "-id")
    serializer = AttendanceRecordSerializer(records, many=True)
    return Response(serializer.data)
