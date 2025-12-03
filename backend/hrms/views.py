from django.http import HttpResponse

def home(request):
    return HttpResponse("HRMS Backend API Running Successfully 🚀")
