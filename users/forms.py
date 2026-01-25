from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Введите email пользователя")
    username = forms.CharField(max_length=50, required=True, label="Введите имя пользователя")
    password1 = forms.CharField(label="Придумайте пароль")
    password2 = forms.CharField(label="Повторите пароль")

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "phone_number",
            "password1",
            "password2",
        )
