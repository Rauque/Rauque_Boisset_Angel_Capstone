import pytest
from apps.catalog.forms import ProductForm
from apps.catalog.models import Category

@pytest.mark.django_db
def test_rn03_formulario_campos_obligatorios():
    cat = Category.objects.create(name="Ventanas")
    data = {
        "name": "Ventana",
        "category": cat.id,
        "material": "ALU",
        "glass_type": "",  # Falta tipo de vidrio
        "thickness": "4",
        "color": "WHT",
        "price": 1000,
        "is_active": True,
        "slug": "",
    }
    form = ProductForm(data)
    assert not form.is_valid()

@pytest.mark.django_db
def test_rn03_formulario_valido():
    cat = Category.objects.create(name="Ventanas")
    data = {
        "name": "Ventana",
        "category": cat.id,
        "material": "ALU",
        "glass_type": "TEM",
        "thickness": "4",
        "color": "WHT",
        "price": 1000,
        "is_active": True,
        "slug": "",
    }
    form = ProductForm(data)
    assert form.is_valid()