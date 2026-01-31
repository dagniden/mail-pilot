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


class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Имя пользователя",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label="Телефон",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        label="Страна",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = CustomUser
        fields = ("username", "phone_number", "avatar", "country")
        widgets = {
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
