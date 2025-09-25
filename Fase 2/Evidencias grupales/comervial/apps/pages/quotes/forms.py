from django import forms
from .models import QuoteRequest, CustomQuoteRequest

class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ["nombre","email","telefono","categoria","mensaje"]
        widgets = {
            "mensaje": forms.Textarea(attrs={"rows":4}),
        }

class CustomQuoteRequestForm(forms.ModelForm):
    class Meta:
        model = CustomQuoteRequest
        fields = ["nombre","email","telefono","tipo","ancho_mm","alto_mm","ubicacion","detalles"]
        widgets = {
            "detalles": forms.Textarea(attrs={"rows":4}),
        }
