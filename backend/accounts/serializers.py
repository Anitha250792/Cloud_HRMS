# backend/accounts/serializers.py
from rest_framework import serializers
from .models import User


class CustomRegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["name", "email", "role", "password1", "password2"]

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({
                "password": "Passwords do not match"
            })
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password1")

        user = User.objects.create_user(
            email=validated_data["email"],
            name=validated_data.get("name", ""),
            role=validated_data.get("role", "EMPLOYEE"),
            password=password,
        )
        return user
