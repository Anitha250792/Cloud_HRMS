# backend/hrms/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class RoleRedirectView(APIView):
    """
    Root URL responds with a simple JSON message.
    No authentication or permissions required.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "HRMS Backend Running"})
