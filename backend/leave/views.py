from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Leave
from .serializers import LeaveSerializer
from employees.models import Employee


class LeaveViewSet(viewsets.ModelViewSet):

    queryset = Leave.objects.all().order_by("-applied_on")
    serializer_class = LeaveSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def apply(self, request):

        employee = Employee.objects.filter(
            is_active=True
        ).first()

        if not employee:
            return Response(
                {"error": "No active employee found"},
                status=400
            )

        try:

            leave = Leave.objects.create(
                employee=employee,
                leave_type=request.data.get("leave_type"),
                start_date=request.data.get("start_date"),
                end_date=request.data.get("end_date"),
                reason=request.data.get("reason"),
                status="PENDING"
            )

            return Response(
                {
                    "message": "Leave applied successfully",
                    "leave_id": leave.id
                },
                status=201
            )

        except Exception as e:

            return Response(
                {"error": str(e)},
                status=500
            )


@api_view(["POST"])
def approve_leave(request, leave_id):

    try:

        leave = Leave.objects.get(id=leave_id)

        leave.status = "APPROVED"
        leave.save()

        return Response(
            {"message": "Leave approved"}
        )

    except Leave.DoesNotExist:

        return Response(
            {"error": "Leave not found"},
            status=404
        )


@api_view(["POST"])
def reject_leave(request, leave_id):

    try:

        leave = Leave.objects.get(id=leave_id)

        leave.status = "REJECTED"
        leave.save()

        return Response(
            {"message": "Leave rejected"}
        )

    except Leave.DoesNotExist:

        return Response(
            {"error": "Leave not found"},
            status=404
        )


@api_view(["GET"])
def my_leaves(request):

    leaves = Leave.objects.all().order_by("-id")

    serializer = LeaveSerializer(
        leaves,
        many=True
    )

    return Response(serializer.data)


@api_view(["GET"])
def pending_leaves(request):

    leaves = Leave.objects.filter(
        status="PENDING"
    ).order_by("-id")

    serializer = LeaveSerializer(
        leaves,
        many=True
    )

    return Response(serializer.data)


@api_view(["GET"])
def leave_balance(request):

    TOTAL = {
        "CASUAL": 12,
        "SICK": 10,
        "EARNED": 15,
        "UNPAID": 0,
    }

    used = {
        "CASUAL": 0,
        "SICK": 0,
        "EARNED": 0,
        "UNPAID": 0,
    }

    balance = {
        key: TOTAL[key] - used[key]
        for key in TOTAL
    }

    return Response({
        "total": TOTAL,
        "used": used,
        "balance": balance
    })