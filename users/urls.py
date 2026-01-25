from django.urls import path

from .views import UserLoginView, UserLogoutView, UserRegisterView

app_name = "users"

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("login/", UserLoginView.as_view(), name="login"),
]
