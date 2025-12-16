from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"


@api_view(["POST"])
def google_auth(request):
    token = request.data.get("credential")

    if not token:
        return Response({"error": "Token missing"}, status=400)

    try:
        # verify google token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        email = idinfo["email"]
        name = idinfo.get("name", "User")

        # if user exists, login
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # default role = EMPLOYEE
            user = User.objects.create_user(
                name=name,
                email=email,
                role="EMPLOYEE",
                password=None  # no password for google login
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
        })

    except Exception as e:
        print("Google Error:", e)
        return Response({"error": "Google authentication failed"}, status=400)
