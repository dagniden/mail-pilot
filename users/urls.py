from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (ProfileView, RegistrationCompleteView, UserDetailView, UserListView, UserLoginView,
                    UserLogoutView, UserRegisterView, VerifyEmailView)

app_name = "users"

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("registration-complete/", RegistrationCompleteView.as_view(), name="registration_complete"),
    path("verify-email/<uuid:code>", VerifyEmailView.as_view(), name="verify_email"),
    # Восстановление пароля (4 этапа)
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("", UserListView.as_view(), name="users"),
    path("<int:pk>/", UserDetailView.as_view(), name="user_detail"),
]
