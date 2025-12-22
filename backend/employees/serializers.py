from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "emp_code",
            "name",
            "email",
            "user_email",
            "department",
            "role",
            "salary",
            "date_joined",
            "is_active",
        ]
