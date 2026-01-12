from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


# =====================================================
# REGISTER SERIALIZER
# =====================================================

class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("name", "email", "role", "password1", "password2")

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password1")
        validated_data.pop("password2")

        user = User.objects.create_user(
            email=validated_data["email"],
            name=validated_data.get("name", ""),
            role=validated_data.get("role", "EMPLOYEE"),
            password=password,
        )
        return user


# =====================================================
# LOGIN SERIALIZER (VERY IMPORTANT FOR 401 ISSUE)
# =====================================================


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(
            email=data["email"],
            password=data["password"],
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data["user"] = user
        return data
