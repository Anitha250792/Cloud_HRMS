from rest_framework import serializers
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):

    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"

    def get_profile_photo_url(self, obj):

        request = self.context.get("request")

        if obj.profile_photo:

            if request:
                return request.build_absolute_uri(
                    obj.profile_photo.url
                )

            return obj.profile_photo.url

        return None