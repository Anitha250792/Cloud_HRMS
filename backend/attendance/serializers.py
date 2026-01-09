from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    working_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ["employee"]



class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee = serializers.CharField(source="employee.name", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "date",
            "check_in",
            "check_out",
            "working_hours",
            "status",
        ]

    def get_status(self, obj):
        if not obj.check_in:
            return "ABSENT"
        if obj.check_in and not obj.check_out:
            return "CHECKED IN"
        if obj.check_in.hour > 10:
            return "LATE"
        return "PRESENT"
