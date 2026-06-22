from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from .views import RoleRedirectView, admin_dashboard_stats, health_check
from accounts.views import RegisterView, LoginView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("health/", health_check),
    path("", RoleRedirectView.as_view(), name="root"),
    path("admin/", admin.site.urls),

    # AUTH (ONLY THIS)
    path("api/auth/register/", RegisterView.as_view()),
    path("api/auth/login/", LoginView.as_view()),

    path(
    "api/dashboard/",
    include("dashboard.urls")
),
  

    # BUSINESS
    path("api/employees/", include("employees.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/payroll/", include("payroll.urls")),
    path("api/leave/", include("leave.urls")),

    # SPA
    path("<path:path>", TemplateView.as_view(template_name="index.html")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )