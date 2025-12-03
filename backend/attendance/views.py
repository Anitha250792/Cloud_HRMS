from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets
from django.utils import timezone
from datetime import date, timedelta
from calendar import monthrange

from .models import Attendance
from .serializers import AttendanceSerializer
from employees.models import Employee


# -----------------------------
#   MAIN VIEWSET (CRUD + Check-in/out + Summaries)
# -----------------------------
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by("-id")
    serializer_class = AttendanceSerializer

    # ---------- CHECK-IN ----------
    @action(methods=["post"], detail=False)
    def check_in(self, request):
        emp_id = request.data.get("employee_id")

        try:
            employee = Employee.objects.get(id=emp_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        attendance = Attendance.objects.create(
            employee=employee,
            check_in=timezone.now(),
        )

        return Response({
            "message": "Check-in successful",
            "data": AttendanceSerializer(attendance).data
        })

    # ---------- CHECK-OUT ----------
    @action(methods=["post"], detail=False)
    def check_out(self, request):
        emp_id = request.data.get("employee_id")

        try:
            employee = Employee.objects.get(id=emp_id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        attendance = Attendance.objects.filter(
            employee=employee,
            check_out__isnull=True
        ).last()

        if not attendance:
            return Response({"error": "No active check-in found"}, status=400)

        attendance.check_out = timezone.now()
        attendance.save()

        return Response({
            "message": "Check-out successful",
            "data": AttendanceSerializer(attendance).data
        })

    # ---------- TODAY SUMMARY ----------
    @action(detail=False, methods=["get"])
    def summary_today(self, request):
        today = date.today()
        total_employees = Employee.objects.count()

        present = Attendance.objects.filter(date=today).values("employee").distinct().count()
        absent = total_employees - present

        late = Attendance.objects.filter(
            date=today,
            check_in__gt=timezone.datetime(today.year, today.month, today.day, 9, 30)
        ).count()

        return Response({
            "date": str(today),
            "total_employees": total_employees,
            "present_today": present,
            "absent_today": absent,
            "late_employees": late,
        })

    # ---------- MONTH SUMMARY ----------
    @action(detail=False, methods=["get"])
    def summary_month(self, request):
        month = int(request.GET.get("month", date.today().month))
        year = int(request.GET.get("year", date.today().year))

        start = date(year, month, 1)
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1)

        records = Attendance.objects.filter(date__gte=start, date__lt=end)

        present_days = records.values("date").distinct().count()

        total_hours = sum(
            [
                (rec.check_out - rec.check_in).total_seconds() / 3600
                for rec in records if rec.check_out
            ],
            0
        )

        return Response({
            "year": year,
            "month": month,
            "total_present_days": present_days,
            "total_hours_worked": round(total_hours, 2),
        })


# -----------------------------
#   TODAY SUMMARY (API standalone)
# -----------------------------
@api_view(["GET"])
def attendance_summary_today(request):
    today = timezone.localdate()
    total_employees = Employee.objects.count()

    present = Attendance.objects.filter(date=today).count()
    absent = total_employees - present

    return Response({
        "date": today,
        "total_employees": total_employees,
        "present_employees": present,
        "absent_employees": absent
    })


# -----------------------------
#   MONTH SUMMARY (API standalone)
# -----------------------------
@api_view(["GET"])
def attendance_summary_month(request):
    today = timezone.localdate()
    year = today.year
    month = today.month

    present_days = Attendance.objects.filter(
        date__year=year,
        date__month=month
    ).count()

    working_days = 22   # optional, can compute dynamically later

    return Response({
        "month": month,
        "year": year,
        "working_days": working_days,
        "total_attendance_marked": present_days,
    })


# -----------------------------
#   HEATMAP API
# -----------------------------
@api_view(["GET"])
def attendance_heatmap(request, emp_id, year, month):
    try:
        employee = Employee.objects.get(id=emp_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    days_in_month = monthrange(year, month)[1]
    heatmap = []

    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)

        record = Attendance.objects.filter(employee=employee, date=current_date).first()

        if record:
            if record.check_in and not record.check_out:
                status_code = "LATE" if record.check_in.hour > 10 else "PRESENT"
            elif record.check_in and record.check_out:
                status_code = "PRESENT"
            else:
                status_code = "ABSENT"
        else:
            status_code = "ABSENT"

        heatmap.append({
            "date": current_date,
            "status": status_code
        })

    return Response(heatmap)


# -----------------------------
#   REAL-TIME CHECK-IN FEED
# -----------------------------
@api_view(["GET"])
def realtime_checkins(request):
    latest = Attendance.objects.order_by("-check_in")[:10]

    data = [
        {
            "employee": item.employee.name,
            "check_in": item.check_in,
            "check_out": item.check_out,
        }
        for item in latest
    ]

    return Response(data)
