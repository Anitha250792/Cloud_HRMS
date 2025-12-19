from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Leave
from .serializers import LeaveSerializer
from employees.models import Employee


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all().order_by("-applied_on")
    serializer_class = LeaveSerializer

    # ================= EMPLOYEE APPLY LEAVE =================
    @action(detail=False, methods=["post"])
    def apply(self, request):
        emp_code = request.data.get("employee")

        if not emp_code:
            return Response(
                {"error": "employee (emp_code) is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            employee = Employee.objects.get(emp_code=emp_code, is_active=True)
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

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
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ================= HR APPROVE =================
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = "APPROVED"
        leave.save()
        return Response({"message": "Leave approved"})

    # ================= HR REJECT =================
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = "REJECTED"
        leave.save()
        return Response({"message": "Leave rejected"})


# ================= EMPLOYEE – MY LEAVES =================
@api_view(["GET"])
def my_leaves(request, emp_code):
    try:
        employee = Employee.objects.get(emp_code=emp_code, is_active=True)
    except Employee.DoesNotExist:
        return Response([], status=status.HTTP_200_OK)

    leaves = Leave.objects.filter(employee=employee).order_by("-applied_on")
    serializer = LeaveSerializer(leaves, many=True)
    return Response(serializer.data)
