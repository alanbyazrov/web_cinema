from users.forms import UserRegisterForm

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView


User = get_user_model()


class CustomLogoutView(TemplateView):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Вы успешно вышли из аккаунта")
        return redirect("users:login")


class SignUpView(CreateView):
    template_name = "users/signup.html"
    form_class = UserRegisterForm

    def get_success_url(self):
        return reverse_lazy("movies:home")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request, "Регистрация прошла успешно! Добро пожаловать!"
        )

        return redirect(self.get_success_url())
