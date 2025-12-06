from rest_framework import serializers
from .models import Payroll

class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_code = serializers.CharField(source="employee.emp_code", read_only=True)
    month_name = serializers.SerializerMethodField()
    net_salary = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = "__all__"

    def get_month_name(self, obj):
        import calendar
        return calendar.month_name[obj.month]

    def get_net_salary(self, obj):
        return obj.net_salary
