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
    path("profile/", ProfileView.as_view(), name="profile"),
    path("", UserListView.as_view(), name="users"),
    path("<int:pk>/", UserDetailView.as_view(), name="user_detail"),
]
