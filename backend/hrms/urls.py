from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter

# Correct ViewSets
from employees.views import EmployeeViewSet
from attendance.views import AttendanceViewSet
from leave.views import LeaveViewSet
from payroll.views import PayrollViewSet

# Correct import for google login
from auth.google_login import google_login

# Router Registration
router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'leaves', LeaveViewSet, basename='leaves')
router.register(r'payroll', PayrollViewSet, basename='payroll')

urlpatterns = [
    path('', lambda request: HttpResponse("HRMS Backend Running 🚀")),

    path('admin/', admin.site.urls),

    # Main auto-generated API routes
    path('api/', include(router.urls)),

    # Custom module URLs
    path("api/leaves/", include("leave.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/scheduler/", include("scheduler.urls")),

    # Google Login
    path("api/auth/google/", google_login),
]
