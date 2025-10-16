# apps/quotes/forms.py
from django import forms
from .models import (
    QuoteRequest, CustomQuoteRequest,
    PRODUCT_TYPES, EDGE_TYPES, FRAME_TYPES, GLASS_TYPES, THICKNESS, PERF_COLOR
)

class QuoteRequestForm(forms.Form):
    nombre = forms.CharField(max_length=150)
    correo = forms.EmailField()
    telefono = forms.CharField(max_length=50)
    mensaje = forms.CharField(widget=forms.Textarea)

    def save(self, commit=True):
        """
        Crea una instancia de QuoteRequest a partir de los campos del formulario.
        """
        data = self.cleaned_data
        return QuoteRequest.objects.create(
            nombre=data.get("nombre", ""),
            email=data.get("correo", ""),
            telefono=data.get("telefono", ""),
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
