from django.conf.urls import url
from django.contrib.auth.views import LoginView, LogoutView
from . import views  # always import views


app_name = "registration"

urlpatterns = [
    url(r"^register/$", views.register, name="register"),
    url(
        r"^register/complete/$",
        views.registration_complete,
        name="registration_complete",
    ),
    url(
        r"^login/$",
        LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    url(
        r"^logout/$",
        LogoutView.as_view(template_name="registration/logged_out.html"),
        name="logout",
    ),
    url(r"^loggedin/$", views.loggedin, name="loggedin"),
]
