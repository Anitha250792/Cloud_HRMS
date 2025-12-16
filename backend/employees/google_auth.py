import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from employees.models import CustomUser


class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("access_token")

        try:
            google_data = requests.get(
                f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
            ).json()

            email = google_data.get("email")
            name = google_data.get("name", "")

            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "role": "EMPLOYEE"
                }
            )

            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role,
                "email": user.email,
                "name": name,
            })
        except Exception:
            return Response({"error": "Google login failed"}, status=400)
