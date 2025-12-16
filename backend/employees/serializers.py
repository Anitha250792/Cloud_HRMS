from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "emp_code",
            "name",
            "email",
            "department",
            "role",
            "salary",
            "date_joined",
            "is_active",
        ]
        read_only_fields = ["id", "is_active"]
