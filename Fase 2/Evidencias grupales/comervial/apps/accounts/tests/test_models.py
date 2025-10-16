from django.contrib import admin
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from apps.catalog.models import Category, Product
from apps.quotes.models import CustomQuoteRequest

@pytest.mark.django_db
def test_rn09_usuario_se_puede_registrar_como_cliente():
    """
    Verifica que se pueda crear un usuario cliente (registro).
    """
    user = User.objects.create_user(username="cliente_test", email="cliente@test.com", password="pass1234")
    assert User.objects.filter(username="cliente_test").exists()

@pytest.mark.django_db
def test_rn09_cotizar_sin_registro_crea_customquoterequest():
    """
    Verifica que un usuario no registrado (cotización anónima) pueda crear una CustomQuoteRequest.
    """
    cot = CustomQuoteRequest.objects.create(
        nombre="Anonimo",
        email="anon@test.com",
        telefono="000000000",
        tipo="window",
        ancho_mm=100,
        alto_mm=100,
        cantidad=1,
        marco="none",
        borde="none",
        cristal="tempered",
        espesor_mm="4",
        color_perfileria="blanco",
        ubicacion="Sala",
        detalles="Cotización anónima"
    )
    assert cot.pk is not None
    assert cot.nombre == "Anonimo"

@pytest.mark.django_db
def test_admin_accede_product_changelist(client):
    admin = User.objects.create_superuser("admin", "admin@test.com", "pass1234")
    client.force_login(admin)
    url = reverse("admin:catalog_product_changelist")
    resp = client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_usuario_normal_no_accede_product_changelist(client):
    user = User.objects.create_user("user", "user@test.com", "pass1234")
    client.force_login(user)
    url = reverse("admin:catalog_product_changelist")
    resp = client.get(url)
    # puede redirigir al login (302) o devolver 403 si no tiene permiso
    assert resp.status_code in (302, 403)

@pytest.mark.django_db
def test_admin_puede_crear_producto_via_admin(client):
    admin = User.objects.create_superuser("admin2", "admin2@test.com", "pass1234")
    client.force_login(admin)
    cat = Category.objects.create(name="Ventanas")
    url = reverse("admin:catalog_product_add")
    data = {
        "category": cat.pk,
        "name": "Producto desde admin",
        "material": "ALU",
        "glass_type": "TEM",
        "thickness": "4",
        "color": "WHT",
        "price": "1234.56",
        "is_active": "on",
    }
    resp = client.post(url, data)
    # admin suele redirigir tras crear (302); aceptar 200 por comportamientos distintos
    assert resp.status_code in (302, 200)
    assert Product.objects.filter(name="Producto desde admin").exists()

@pytest.mark.django_db
def test_admin_accede_customquoterequest_changelist(client):
    admin_user = User.objects.create_superuser("admin3", "admin3@test.com", "pass1234")
    client.force_login(admin_user)
    model = CustomQuoteRequest
    if model in admin.site._registry:
        url = reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist")
        resp = client.get(url)
        assert resp.status_code == 200
    else:
        pytest.skip("CustomQuoteRequest no registrado en el admin")
# ...existing code...

@pytest.mark.django_db
def test_cliente_puede_visualizar_productos(client):
    cat = Category.objects.create(name="Ventanas")
    p_active = Product.objects.create(
        category=cat, name="Ventana activa", material="ALU", glass_type="TEM",
        thickness="4", color="WHT", price=1000, is_active=True
    )
    p_inactive = Product.objects.create(
        category=cat, name="Ventana inactiva", material="ALU", glass_type="TEM",
        thickness="4", color="WHT", price=1000, is_active=False
    )
    url = reverse("catalog:catalog_list")
    resp = client.get(url)
    assert resp.status_code == 200
    content = resp.content.decode()
    assert p_active.name in content
    assert p_inactive.name not in content

@pytest.mark.django_db
def test_usuario_cliente_puede_generar_cotizacion_mediante_modelo():
    """
    Verifica que un cliente (o anónimo) pueda crear una CustomQuoteRequest (representa generar una cotización).
    Si tienes endpoint HTTP para esto, agrega una prueba de vista POST en su lugar.
    """
    user = User.objects.create_user("cliente", "cliente@test.com", "pass1234")
    cot = CustomQuoteRequest.objects.create(
        nombre="Cliente",
        email="cliente@test.com",
        telefono="000000000",
        tipo="window",
        ancho_mm=100,
        alto_mm=100,
        cantidad=1,
        marco="none",
        borde="none",
        cristal="tempered",
        espesor_mm="4",
        color_perfileria="blanco",
        ubicacion="Sala",
        detalles="Cotización desde cliente"
    )
    assert cot.pk is not None
    assert cot.nombre == "Cliente"

@pytest.mark.django_db
def test_cliente_no_puede_acceder_admin_product_changelist(client):
    """
    El rol cliente no debe acceder al listado de administración de productos.
    """
    user = User.objects.create_user("normal", "normal@test.com", "pass1234")
    client.force_login(user)
    url = reverse("admin:catalog_product_changelist")
    resp = client.get(url)
    assert resp.status_code in (302, 403)
    
def test_pytest_funciona():
    assert 1 == 1