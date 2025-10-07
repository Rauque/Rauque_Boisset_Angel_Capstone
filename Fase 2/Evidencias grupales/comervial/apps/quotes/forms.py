# apps/quotes/forms.py
from django import forms
from .models import (
    QuoteRequest, CustomQuoteRequest,
    PRODUCT_TYPES, EDGE_TYPES, FRAME_TYPES, GLASS_TYPES, THICKNESS, PERF_COLOR
)

class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ["nombre","email","telefono","categoria","mensaje"]
        widgets = {"mensaje": forms.Textarea(attrs={"rows":4})}

class CustomQuoteRequestForm(forms.ModelForm):
    class Meta:
        model = CustomQuoteRequest
        fields = [
            "nombre","email","telefono","tipo",
            "ancho_mm","alto_mm","cantidad",
            "marco","borde",            # espejo
            "cristal","espesor_mm","color_perfileria",  # ventana
            "ubicacion","detalles",
        ]
        widgets = {
            "detalles": forms.Textarea(attrs={"rows":4}),
        }

    # reglas condicionales
    def clean(self):
        data = super().clean()
        t = data.get("tipo")
        if not t:
            return data

        if data.get("cantidad") in (None, 0):
            data["cantidad"] = 1

        if t == "mirror":
            if not data.get("marco"):
                self.add_error("marco", "Selecciona si lleva marco o no.")
            if data.get("marco") == "none" and not data.get("borde"):
                self.add_error("borde", "Indica el tipo de borde.")
            # limpiar campos de ventana para evitar “ruido”
            for f in ("cristal", "espesor_mm", "color_perfileria"):
                if not data.get(f):
                    data[f] = ""
        elif t == "window":
            for f in ("cristal", "espesor_mm", "color_perfileria"):
                if not data.get(f):
                    self.add_error(f, "Campo obligatorio para ventana.")
            # limpiar campos de espejo
            for f in ("marco", "borde"):
                if not data.get(f):
                    data[f] = ""
        return data
