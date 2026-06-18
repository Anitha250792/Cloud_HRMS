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
    try:
        employees = Employee.objects.filter(
            is_active=True
        ).select_related("user")

        serializer = EmployeeSerializer(
            employees,
            many=True
        )

        return Response(serializer.data)

    except Exception as e:

        print(
            "EMPLOYEE LIST ERROR:",
            str(e)
        )

        return Response(
            {
                "error":
                "Internal server error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===================== CREATE EMPLOYEE =====================
@api_view(["POST"])
def create_employee(request):

    try:

        email = request.data.get("email")

        if not email:

            return Response(
                {
                    "email":
                    ["Email is required"]
                },
                status=400
            )

        # Create User

        user, user_created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": request.data.get(
                    "name",
                    ""
                ),
                "role": "EMPLOYEE",
            },
        )

        if user_created:

            user.set_password(
                "Default@123"
            )

            user.save()

        # Create Employee

        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults={
                "emp_code": request.data.get(
                    "emp_code"
                ),
                "name": request.data.get(
                    "name"
                ),
                "email": email,
                "department": request.data.get(
                    "department"
                ),
                "role": request.data.get(
                    "role"
                ),
                "salary": request.data.get(
                    "salary"
                ),
                "date_joined": request.data.get(
                    "date_joined"
                ),
                "is_active": True,
            },
        )

        if not created:

            employee.is_active = True

            employee.save()

            return Response(
                {
                    "message":
                    "Employee already exists and reactivated",
                    "employee_id":
                    employee.id,
                }
            )

        return Response(
            {
                "message":
                "Employee created successfully",
                "employee_id":
                employee.id,
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:

        print(
            "CREATE ERROR:",
            str(e)
        )

        return Response(
            {
                "error":
                str(e)
            },
            status=500
        )


# ===================== UPDATE EMPLOYEE =====================
@api_view(["PUT"])
def update_employee(request, pk):

    try:

        employee = Employee.objects.get(
            pk=pk,
            is_active=True
        )

        serializer = EmployeeSerializer(
            employee,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data
        )

    except Employee.DoesNotExist:

        return Response(
            {
                "error":
                "Employee not found"
            },
            status=404
        )


# ===================== DELETE EMPLOYEE =====================
@api_view(["DELETE"])
def delete_employee(request, pk):

    try:

        employee = Employee.objects.get(
            pk=pk
        )

        employee.is_active = False

        employee.save()

        return Response(
            {
                "message":
                "Employee deleted successfully"
            }
        )

    except Employee.DoesNotExist:

        return Response(
            {
                "error":
                "Employee not found"
            },
            status=404
        )


# ===================== GET SINGLE EMPLOYEE =====================
@api_view(["GET"])
def get_employee(request, pk):

    try:

        employee = Employee.objects.get(
            pk=pk,
            is_active=True
        )

        serializer = EmployeeSerializer(
            employee
        )

        return Response(
            serializer.data
        )

    except Employee.DoesNotExist:

        return Response(
            {
                "error":
                "Employee not found"
            },
            status=404
        )