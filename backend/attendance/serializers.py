from rest_framework import serializers
from .models import Attendance



class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee = serializers.CharField(source="employee.name", read_only=True)
    hours_worked = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "check_in",
            "check_out",
            "hours_worked",
            "status",
        ]

    def get_hours_worked(self, obj):
        if obj.check_in and obj.check_out:
            diff = obj.check_out - obj.check_in
            return round(diff.total_seconds() / 3600, 2)
        return None

    def get_status(self, obj):
        if not obj.check_in:
            return "ABSENT"
        if obj.check_in and not obj.check_out:
            return "PRESENT"
        if obj.check_in.hour > 10:
            return "LATE"
        return "PRESENT"
