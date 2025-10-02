from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "slug", "category",
            "material", "glass_type", "thickness", "color",
            "price", "is_active", "image",
        ]
