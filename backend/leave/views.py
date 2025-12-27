from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Leave
from .serializers import LeaveSerializer
from employees.models import Employee


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all().order_by("-applied_on")
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    # ================= EMPLOYEE APPLY LEAVE =================
    @action(detail=False, methods=["post"])
    def apply(self, request):
        employee = Employee.objects.filter(
            user=request.user,
            is_active=True
        ).first()

        if not employee:
            return Response(
                {"error": "Employee profile not linked to this account"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveSerializer(data={
            "leave_type": request.data.get("leave_type"),
            "start_date": request.data.get("start_date"),
            "end_date": request.data.get("end_date"),
            "reason": request.data.get("reason"),
            "status": "PENDING",
        })

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


        serializer.save(employee=employee)

        return Response(
            {"message": "Leave applied successfully"},
            status=status.HTTP_201_CREATED,
        )

    # ================= HR APPROVE =================
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        if request.user.role != "HR":
            return Response({"error": "Unauthorized"}, status=403)

        leave = self.get_object()
        leave.status = "APPROVED"
        leave.save()
        return Response({"message": "Leave approved"})

    # ================= HR REJECT =================
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        if request.user.role != "HR":
            return Response({"error": "Unauthorized"}, status=403)

        leave = self.get_object()
        leave.status = "REJECTED"
        leave.save()
        return Response({"message": "Leave rejected"})


# ================= EMPLOYEE – MY LEAVES =================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_leaves(request):
    employee = Employee.objects.filter(user=request.user).first()
    if not employee:
        return Response([], status=200)

    leaves = Leave.objects.filter(employee=employee).order_by("-applied_on")
    serializer = LeaveSerializer(leaves, many=True)
    return Response(serializer.data)
