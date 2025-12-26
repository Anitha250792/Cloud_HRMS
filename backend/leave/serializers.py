from rest_framework import serializers
from .models import Leave

class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    emp_code = serializers.CharField(source="employee.emp_code", read_only=True)

    class Meta:
        model = Leave
        fields = [
            "id",
            "employee",
            "employee_name",
            "emp_code",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "applied_on",
        ]
        read_only_fields = ["employee", "status", "applied_on"]
