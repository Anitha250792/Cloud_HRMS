from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterSerializer, LoginSerializer


# =====================================================
# REGISTER VIEW
# =====================================================

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Registration successful"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====================================================
# LOGIN VIEW
# =====================================================

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=3600,
        )

        return response