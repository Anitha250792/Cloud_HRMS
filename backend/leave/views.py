from django.db.models import Q Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import timedelta

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
    employee = Employee.objects.filter(user=request.user, is_active=True).first()
    if not employee:
        return Response({"error": "Employee profile missing"}, status=400)

    overlap = Leave.objects.filter(
        employee=employee,
        status__in=["PENDING", "APPROVED"],
        start_date__lte=request.data["end_date"],
        end_date__gte=request.data["start_date"],
    )

    if overlap.exists():
        return Response(
            {"error": "Overlapping leave already applied"},
            status=400
        )

    serializer = LeaveSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(employee=employee, status="PENDING")

    return Response({"message": "Leave applied successfully"}, status=201)


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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def leave_balance(request):
    employee = Employee.objects.filter(user=request.user).first()
    if not employee:
        return Response({"balance": 0})

    approved_leaves = Leave.objects.filter(
        employee=employee,
        status="APPROVED"
    )

    used_days = sum(l.total_days() for l in approved_leaves)

    TOTAL_LEAVES = 24   # yearly policy
    balance = TOTAL_LEAVES - used_days

    return Response({
        "total": TOTAL_LEAVES,
        "used": used_days,
        "balance": max(balance, 0),
    })


