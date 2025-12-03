from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID_HERE"


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@api_view(["POST"])
def google_login(request):
    try:
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token missing"}, status=400)

        # Validate token with Google
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        email = idinfo["email"]
        name = idinfo.get("name")

        # Create user if not exists
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "first_name": name}
        )

        # Issue JWT tokens
        tokens = get_tokens_for_user(user)

        return Response(
            {
                "message": "Login successful",
                "token": tokens,
                "email": email,
                "name": name,
            },
            status=200,
        )

    except Exception as e:
        print("Google login error:", e)
        return Response({"error": "Invalid token"}, status=400)
