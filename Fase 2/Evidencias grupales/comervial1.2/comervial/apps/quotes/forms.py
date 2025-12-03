# apps/quotes/forms.py
from django import forms
from .models import (
    QuoteRequest, CustomQuoteRequest,
    PRODUCT_TYPES, EDGE_TYPES, FRAME_TYPES, GLASS_TYPES, THICKNESS, PERF_COLOR
)

class QuoteRequestForm(forms.Form):
    CATEGORIAS = [
        ("ventanas", "Ventanas"),
        ("cristales", "Cristales"),
        ("shower", "Shower door"),
        ("mamparas", "Mamparas"),
        ("otros", "Otros"),
    ]

    nombre = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # ⚠️ renombrado de 'correo' a 'email' para que calce con el template
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    telefono = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    categoria = forms.ChoiceField(
        choices=CATEGORIAS,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4})
    )

    def save(self, commit=True):
        data = self.cleaned_data
        return QuoteRequest.objects.create(
            nombre=data.get("nombre", ""),
            email=data.get("email", ""),   # ← ahora mapea a 'email'
            telefono=data.get("telefono", ""),
            categoria=data.get("categoria", ""),
            mensaje=data.get("mensaje", "")
        )

class CustomQuoteRequestForm(forms.ModelForm):
    class Meta:
        model = CustomQuoteRequest
        fields = [
            "nombre", "email", "telefono", "tipo",
            "ancho_mm", "alto_mm", "cantidad",
            "marco", "borde", "cristal", "espesor_mm",
            "color_perfileria", "ubicacion", "detalles",
        ]

# Alias de compatibilidad: ContactForm esperado por los tests
ContactForm = QuoteRequestForm
