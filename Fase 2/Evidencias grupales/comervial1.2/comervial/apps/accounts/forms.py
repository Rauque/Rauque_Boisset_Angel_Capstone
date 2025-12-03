from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import CustomerProfile
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

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = [
            "full_name",
            "rut",
            "phone",
            "address",
            "comuna",
            "region",
        ]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "rut": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "id_customer_rut",          # <- ID fijo
                    "placeholder": "12.345.678-9",
                    "inputmode": "text",
                    "pattern": r"\d{1,2}\.\d{3}\.\d{3}-[\dKk]",
                    "title": "Formato esperado: 12.345.678-9",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+56 912345678",
                    "inputmode": "tel",
                }
            ),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "comuna": forms.TextInput(attrs={"class": "form-control"}),
            "region": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "full_name": "Nombre completo",
            "rut": "RUT",
            "phone": "Teléfono",
            "address": "Dirección",
            "comuna": "Comuna",
            "region": "Región",
        }

    # ---------- RUT: validar y formatear 12.345.678-9 ----------
    def clean_rut(self):
        rut = (self.cleaned_data.get("rut") or "").strip()

        if not rut:
            return ""

        # quitar puntos y guión
        rut = rut.replace(".", "").replace("-", "").upper()

        # debe ser 7 u 8 dígitos + dígito verificador (0–9 o K)
        if not re.match(r"^\d{7,8}[0-9K]$", rut):
            raise forms.ValidationError("RUT inválido. Usa formato 12.345.678-9.")

        cuerpo = rut[:-1]
        dv_ingresado = rut[-1]

        # cálculo dígito verificador (módulo 11)
        suma = 0
        factor = 2
        for d in reversed(cuerpo):
            suma += int(d) * factor
            factor += 1
            if factor > 7:
                factor = 2
        resto = suma % 11
        dv_calc = 11 - resto
        if dv_calc == 11:
            dv_calc_str = "0"
        elif dv_calc == 10:
            dv_calc_str = "K"
        else:
            dv_calc_str = str(dv_calc)

        if dv_ingresado != dv_calc_str:
            raise forms.ValidationError("RUT inválido (dígito verificador incorrecto).")

        # formatear como 12.345.678-9
        cuerpo_rev = cuerpo[::-1]
        partes = [cuerpo_rev[i : i + 3] for i in range(0, len(cuerpo_rev), 3)]
        cuerpo_formateado = ".".join(p[::-1] for p in partes[::-1])
        return f"{cuerpo_formateado}-{dv_ingresado}"

    # ---------- Teléfono: siempre +56 + 9 dígitos ----------
    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()

        if not phone:
            return ""

        # dejar solo dígitos
        digits = re.sub(r"\D", "", phone)

        # sacar prefijos que la gente suele escribir
        if digits.startswith("56"):
            digits = digits[2:]
        if digits.startswith("0"):
            digits = digits[1:]

        # ahora deberían quedar EXACTAMENTE 9 dígitos
        if len(digits) != 9:
            raise forms.ValidationError(
                "El teléfono debe tener 9 dígitos (sin contar el +56)."
            )

        # guardar siempre en formato +569XXXXXXXX (sin espacios)
        return f"+56{digits}"