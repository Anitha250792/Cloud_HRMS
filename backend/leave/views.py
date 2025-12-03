from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Count

from .models import Leave
from .serializers import LeaveSerializer
from employees.models import Employee


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all().order_by("-applied_on")
    serializer_class = LeaveSerializer

    # APPLY LEAVE
    @action(detail=False, methods=["post"])
    def apply(self, request):

        emp_code = request.data.get("employee")

        try:
            employee = Employee.objects.get(emp_code=emp_code)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=404)

        data = {
            "employee": employee.id,
            "leave_type": request.data.get("leave_type"),
            "start_date": request.data.get("start_date"),
            "end_date": request.data.get("end_date"),
            "reason": request.data.get("reason"),
            "status": "PENDING",
        }

        serializer = LeaveSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Leave applied successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # APPROVE LEAVE
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = "APPROVED"
        leave.save()
        return Response({"message": "Leave Approved ✔"}, status=200)

    # REJECT LEAVE
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = "REJECTED"
        leave.save()
        return Response({"message": "Leave Rejected ✖"}, status=200)


# ANALYTICS
@api_view(["GET"])
def leave_type_distribution(request):
    data = Leave.objects.values("leave_type").annotate(total=Count("leave_type"))
    return Response({item["leave_type"]: item["total"] for item in data})


@api_view(["GET"])
def leave_monthly_trend(request):
    data = (
        Leave.objects.extra(select={'month': "EXTRACT(MONTH FROM start_date)"})
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )
    return Response([
        {"month": int(item["month"]), "total": item["total"]} for item in data
    ])
