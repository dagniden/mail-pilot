from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from .forms import CustomUserCreationForm, ProfileUpdateForm
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


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CustomUser
    permission_required = ["campaigns.can_view_all_recipients"]


class UserDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = CustomUser
    permission_required = ["campaigns.can_view_all_recipients"]
    context_object_name = "user_detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_obj = self.get_object()

        context["total_clients"] = user_obj.clients.count()
        context["total_campaigns"] = user_obj.campaigns.count()
        context["total_templates"] = user_obj.templates.count()

        return context

    def post(self, request, *args, **kwargs):
        user_obj = self.get_object()

        if user_obj == request.user:
            messages.error(request, "Нельзя заблокировать самого себя")
            return redirect(user_obj.get_absolute_url())

        if "toggle_active" in request.POST:
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            if user_obj.is_active:
                messages.success(request, f"Пользователь {user_obj.email} разблокирован")
            else:
                messages.warning(request, f"Пользователь {user_obj.email} заблокирован")
        return redirect(user_obj.get_absolute_url())


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
            messages.error(request, "Ссылка подтверждения истекла (24 часа). Пожалуйста, зарегистрируйтесь заново.")
            return redirect("users:register")

        user.is_email_verified = True
        user.is_active = True
        user.save(update_fields=["is_email_verified", "is_active"])

        messages.success(request, "Email успешно подтверждён! Теперь вы можете войти в систему.")

        return redirect("users:login")


class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлён")
        return super().form_valid(form)
