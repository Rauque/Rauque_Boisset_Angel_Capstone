import pytest
from apps.catalog.models import Product, Category
'''RN-01: Cada producto del catálogo (ventanas, espejos, puertas de vidrio, etc.) debe
tener un identificador único, descripción, dimensiones, tipo de vidrio, marco y precio
base.'''
@pytest.mark.django_db
def test_rn01_producto_campos_obligatorios():
    cat = Category.objects.create(name="Ventanas")
    prod = Product.objects.create(
        category=cat, name="Ventana", material="ALU", glass_type="TEM",
        thickness="4", color="WHT", price=1000
    )
    assert prod.name == "Ventana"
    assert prod.material == "ALU"
    assert prod.glass_type == "TEM"
    assert prod.price == 1000
'''RN-02: Los precios de los productos se calculan automáticamente en función de las dimensiones y materiales seleccionados por el cliente. '''
@pytest.mark.django_db
def test_rn02_precio_calculado():
    # Suponiendo que tienes un método para calcular el precio
    cat = Category.objects.create(name="Puertas")
    prod = Product(
        category=cat, name="Puerta", material="ALU", glass_type="TEM",
        thickness="4", color="WHT"
    )
    prod.calcular_precio()
    assert prod.price > 0

'''RN-17: Los productos personalizados deben ser aprobados antes de confirmarse la
cotización.
'''
@pytest.mark.django_db
def test_rn17_imagen_asociada():
    cat = Category.objects.create(name="Espejos")
    prod = Product.objects.create(
        category=cat, name="Espejo", material="ALU", glass_type="TEM",
        thickness="4", color="WHT", price=500, image="products/espejo.jpg"
    )
    assert prod.image.name == "products/espejo.jpg"

def test_pytest_funciona():
    assert 1 == 1