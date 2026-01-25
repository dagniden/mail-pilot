
from django.contrib.auth.views import LoginView, LogoutView

from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm


class UserRegisterView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("home")


class UserLogoutView(LogoutView):
    next_page = "home"


class UserLoginView(LoginView):
    template_name = "users/login.html"
