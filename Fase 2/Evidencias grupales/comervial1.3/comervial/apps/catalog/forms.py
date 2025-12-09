from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "slug", "category",
            "material", "glass_type", "thickness", "color",
            "description",             
            "price", "is_active", "image",
        ]
        labels = {
            "description": "Descripción",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe brevemente este producto…",
                }
            ),
        }
