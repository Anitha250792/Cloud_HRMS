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
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is inactive")

        data["user"] = user
        return data