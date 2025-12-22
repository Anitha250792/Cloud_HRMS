from rest_framework import serializers
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)

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
            "user_id",
            "user_email",
            "user_role",
        ]
        read_only_fields = ["id", "is_active"]
