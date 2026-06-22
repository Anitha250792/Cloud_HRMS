from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from .models import Employee
from .serializers import EmployeeSerializer

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_employees(request):

    employees = Employee.objects.filter(
        is_active=True
    ).select_related("user")

    serializer = EmployeeSerializer(
        employees,
        many=True
    )

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_employee(request, pk):

    try:

        employee = Employee.objects.get(
            pk=pk,
            is_active=True
        )

        serializer = EmployeeSerializer(employee)

        return Response(serializer.data)

    except Employee.DoesNotExist:

        return Response(
            {"error": "Employee not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_employee(request):

    try:

        email = request.data.get("email")

        if not email:

            return Response(
                {"error": "Email required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": request.data.get("name", ""),
                "role": "EMPLOYEE",
            }
        )

        if created:
            user.set_password("Default@123")
            user.save()

        employee = Employee.objects.create(

            user=user,

            emp_code=request.data.get("emp_code"),
            name=request.data.get("name"),
            profile_photo=request.FILES.get(
    "profile_photo"
),
            email=email,

            phone=request.data.get("phone"),
            gender=request.data.get("gender"),
            dob=request.data.get("dob"),
            marital_status=request.data.get("marital_status"),
            address=request.data.get("address"),
            emergency_contact=request.data.get("emergency_contact"),

            department=request.data.get("department"),
            role=request.data.get("role"),
            designation=request.data.get("designation"),
            employment_type=request.data.get("employment_type"),
            reporting_manager=request.data.get("reporting_manager"),
            date_joined=request.data.get("date_joined"),

            salary=request.data.get("salary"),

            bank_name=request.data.get("bank_name"),
            bank_account=request.data.get("bank_account"),
            ifsc_code=request.data.get("ifsc_code"),
            pan_number=request.data.get("pan_number"),
            pf_number=request.data.get("pf_number"),

            is_active=True,
        )

        return Response(
    EmployeeSerializer(
        employee,
        context={"request": request}
    ).data,
    status=status.HTTP_201_CREATED
)

    except Exception as e:
        print("CREATE EMPLOYEE ERROR:", str(e))

        return Response(
            {"error": str(e)},
            status=500
        )

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
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

        return Response(serializer.data)

    except Employee.DoesNotExist:

        return Response(
            {"error": "Employee not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_employee(request, pk):

    try:

        employee = Employee.objects.get(pk=pk)

        employee.is_active = False
        employee.save()

        return Response(
            {"message": "Employee deleted successfully"}
        )

    except Employee.DoesNotExist:

        return Response(
            {"error": "Employee not found"},
            status=status.HTTP_404_NOT_FOUND
        )