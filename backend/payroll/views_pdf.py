from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Payroll
from .utils import generate_payroll_pdf
import tempfile

def download_payslip(request, pk):
    payroll = get_object_or_404(Payroll, id=pk)

    temp = tempfile.NamedTemporaryFile(delete=True, suffix=".pdf")
    generate_payroll_pdf(payroll, temp.name)

    temp.seek(0)
    response = HttpResponse(temp.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Payslip_{payroll.employee.name}_{payroll.month}_{payroll.year}.pdf"'
    return response
