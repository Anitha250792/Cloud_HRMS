from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from .models import Employee
from .serializers import EmployeeSerializer

User = get_user_model()


# ===================== LIST EMPLOYEES =====================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_employees(request):
    if request.user.role != "HR":
        raise PermissionDenied("Only HR can view employees")

    employees = (
        Employee.objects
        .filter(is_active=True)
        .select_related("user")
        .order_by("-id")
    )

    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)


# ===================== CREATE EMPLOYEE =====================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_employee(request):
    if request.user.role != "HR":
        raise PermissionDenied("Only HR can add employees")

    email = request.data.get("email")
    if not email:
        return Response({"email": ["Email is required"]}, status=400)

    # ---- USER (AUTH) ----
    user, user_created = User.objects.get_or_create(
        email=email,
        defaults={
            "name": request.data.get("name", ""),
            "role": "EMPLOYEE",
        },
    )

    if user_created:
        user.set_password("Default@123")
        user.save()

    # ---- EMPLOYEE (PROFILE) ----
    employee, created = Employee.objects.get_or_create(
        user=user,
        defaults={
            "emp_code": request.data.get("emp_code"),
            "name": request.data.get("name"),
            "email": email,
            "department": request.data.get("department"),
            "role": request.data.get("role"),
            "salary": request.data.get("salary"),
            "date_joined": request.data.get("date_joined"),
            "is_active": True,
        },
    )

    if not created:
        employee.is_active = True
        employee.save()
        return Response(
            {
                "message": "Employee already existed and reactivated",
                "employee_id": employee.id,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {
            "message": "Employee created successfully",
            "employee_id": employee.id,
        },
        status=status.HTTP_201_CREATED,
    )


# ===================== UPDATE =====================
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_employee(request, pk):
    if request.user.role != "HR":
        raise PermissionDenied("Only HR can update employees")

    try:
        employee = Employee.objects.get(pk=pk, is_active=True)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)


# ===================== DELETE (SOFT) =====================
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_employee(request, pk):
    if request.user.role != "HR":
        raise PermissionDenied("Only HR can delete employees")

    try:
        employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    employee.is_active = False
    employee.save()
    return Response({"message": "Employee deactivated"})
