from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo ya está registrado.")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1") or ""
        p2 = self.cleaned_data.get("password2") or ""

        if p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")

        # Largo 8–16
        if not (8 <= len(p1) <= 16):
            raise ValidationError("La contraseña debe tener entre 8 y 16 caracteres.")

        # Al menos una letra y un número
        if not re.search(r"[A-Za-z]", p1) or not re.search(r"\d", p1):
            raise ValidationError("Debe incluir al menos una letra y un número.")

        return p2
