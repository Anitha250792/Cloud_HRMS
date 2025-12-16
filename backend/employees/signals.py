from django.dispatch import receiver
from allauth.account.signals import user_logged_in
from django.shortcuts import redirect

@receiver(user_logged_in)
def redirect_user_after_login(request, user, **kwargs):
    if user.role == "HR":
        request.session["redirect_to"] = "/hr/dashboard/"
    else:
        request.session["redirect_to"] = "/employee/dashboard/"
