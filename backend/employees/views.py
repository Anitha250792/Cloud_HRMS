from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Employee
from .serializers import EmployeeSerializer

User = get_user_model()


# ===================== LIST EMPLOYEES =====================
@api_view(["GET"])
def list_employees(request):
    employees = Employee.objects.filter(is_active=True)
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)


# ===================== CREATE / EDIT EMPLOYEE =====================
@api_view(["POST"])
def create_employee(request):
    email = request.data.get("email")

    if not email:
        return Response({"email": ["Email is required"]}, status=400)

    # 🔹 Get or create USER
    user, user_created = User.objects.get_or_create(
        email=email,
        defaults={
            "name": request.data.get("name", ""),
            "role": "EMPLOYEE"
        }
    )

    if user_created:
        user.set_password("Default@123")
        user.save()

    # 🔹 Check if EMPLOYEE already exists
    employee = Employee.objects.filter(email=email, is_active=True).first()

    if employee:
        return Response(
            {
                "message": "Employee already exists",
                "action": "edit",
                "employee_id": employee.id
            },
            status=status.HTTP_200_OK
        )

    # 🔹 Create NEW employee
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        employee = serializer.save(user=user)
        return Response(
            {
                "message": "Employee created successfully",
                "action": "created",
                "employee_id": employee.id
            },
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=400)


# ===================== UPDATE =====================
@api_view(["PUT"])
def update_employee(request, pk):
    try:
        emp = Employee.objects.get(pk=pk, is_active=True)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)

    serializer = EmployeeSerializer(emp, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


# ===================== DELETE (SOFT) =====================
@api_view(["DELETE"])
def delete_employee(request, pk):
    try:
        emp = Employee.objects.get(pk=pk)
        emp.is_active = False
        emp.save()
        return Response({"message": "Employee deactivated"})
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=404)
