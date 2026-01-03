from django.db.models import Q, Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date
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

        # ❌ Prevent overlapping leave dates
        overlap = Leave.objects.filter(
            employee=employee,
            status__in=["PENDING", "APPROVED"]
        ).filter(
            Q(start_date__lte=request.data.get("end_date")) &
            Q(end_date__gte=request.data.get("start_date"))
        )

        if overlap.exists():
            return Response(
                {"error": "Leave dates overlap with an existing leave"},
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
            return Response(serializer.errors, status=400)

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
    leaves = Leave.objects.filter(employee=request.user).order_by("-id")
    serializer = LeaveSerializer(leaves, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def leave_balance(request):
    YEARLY_QUOTA = 12

    used = Leave.objects.filter(
        employee=request.user,
        status="APPROVED",
        start_date__year=date.today().year
    ).aggregate(total=Sum("days"))["total"] or 0

    balance = max(YEARLY_QUOTA - used, 0)

    return Response({
        "used": used,
        "balance": balance
    })
