from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import generate_monthly_payroll

@api_view(["POST"])
def run_payroll_scheduler(request):
    message = generate_monthly_payroll()
    return Response({"status": message})
