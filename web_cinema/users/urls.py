from users.forms import MyLoginForm
from users.views import (  # Импортируем наш кастомный view
    CustomLogoutView,
    SignUpView,
)

from django.contrib.auth import views
from django.urls import path


app_name = "users"

urlpatterns = [
    path(
        "login/",
        views.LoginView.as_view(
            template_name="users/login.html",
            form_class=MyLoginForm,
        ),
        name="login",
    ),
    path(
        "logout/",
        CustomLogoutView.as_view(),  # Используем наш кастомный view
        name="logout",
    ),
    path(
        "signup/",
        SignUpView.as_view(),
        name="signup",
    ),
]
