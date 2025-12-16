from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()

# ------------------------------------------------------
# REGISTER USER
# ------------------------------------------------------
@api_view(["POST"])
def register_user(request):
    name = request.data.get("name")
    email = request.data.get("email")
    role = request.data.get("role")
    password1 = request.data.get("password1")
    password2 = request.data.get("password2")

    # Check all fields
    if not all([name, email, role, password1, password2]):
        return Response({"error": "All fields are required"}, status=400)

    # Password mismatch
    if password1 != password2:
        return Response({"error": "Passwords do not match"}, status=400)

    # Email exists
    if User.objects.filter(email=email).exists():
        return Response({"email": ["Email already exists"]}, status=400)

    # Create user
    user = User.objects.create_user(
        name=name,
        email=email,
        password=password1,
        role=role
    )

    # Generate tokens
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "message": "User registered successfully",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
        },
        status=status.HTTP_201_CREATED,
    )


# ------------------------------------------------------
# LOGIN USER
# ------------------------------------------------------
@api_view(["POST"])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password required"}, status=400)

    # Find user
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid login credentials"}, status=400)

    # Authenticate using email
    user = authenticate(username=user_obj.email, password=password)

    if not user:
        return Response({"error": "Invalid login credentials"}, status=400)

    # Generate tokens
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
        }
    )

GOOGLE_CLIENT_ID = "437563404520-kft1nf9judspf4mk907hrg70c1drqpm3.apps.googleusercontent.com"

@api_view(["POST"])
def google_login(request):
    try:
        credential = request.data.get("credential")
        if not credential:
            return Response({"error": "Missing credential"}, status=400)

        # Verify token from Google
        idinfo = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo["email"]
        name = idinfo.get("name", "Google User")

        # If user exists → login
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # If no user → create one
            user = User.objects.create_user(
                name=name,
                email=email,
                password="google-auth",  # dummy password
                role="EMPLOYEE"
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
            "message": "Google login success"
        })

    except Exception as e:
        print("GOOGLE LOGIN ERROR:", e)
        return Response({"error": "Google login failed"}, status=400)