from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import CustomUserCreationForm
from .models import CustomUser
from .services import EmailVerificationService


class UserRegisterView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        EmailVerificationService.send_verification(user, self.request)
        messages.success(self.request, f"Письмо отправлено на {user.email}")

        return redirect("users:registration_complete")


class UserLogoutView(LogoutView):
    next_page = "home"


class UserLoginView(LoginView):
    template_name = "users/login.html"


class RegistrationCompleteView(TemplateView):
    template_name = "users/registration_complete.html"


class VerifyEmailView(TemplateView):
    template_name = "users/verify_email.html"

    def get(self, request, code):
        """Активация пользователя при GET-запросе"""
        user = get_object_or_404(CustomUser, verification_code=code)

        if user.is_email_verified:
            messages.info(request, "Email уже подтверждён ранее.")
            return redirect("users:login")

        if user.is_verification_expired():
            messages.error(request, "Ссылка подтверждения истекла. Запросите новую.")
            return redirect("users:resend_verification")

        user.is_email_verified = True
        user.is_active = True
        user.save(update_fields=["is_email_verified", "is_active"])

        messages.success(request, "Email успешно подтверждён! Теперь вы можете войти в систему.")

        return redirect("users:login")
