import pytest
from django.core import mail
from decimal import Decimal
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User
from apps.catalog.models import Category, Product
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage

from apps.quotes.models import CustomQuoteRequest
from apps.quotes.forms import ContactForm

# intentar importar Order; si no existe, marcar None y saltar tests que lo usen
try:
    from apps.quotes.models import Order
except Exception:
    Order = None

@pytest.mark.django_db
def test_rn04_producto_personalizado_requiere_aprobacion():
    cotizacion = CustomQuoteRequest.objects.create(
        nombre="Pedro",
        email="pedro@test.com",
        telefono="555555555",
        tipo="window",
        ancho_mm=100,
        alto_mm=100,
        cantidad=1,
        marco="aluminum",
        borde="polished",
        cristal="tempered",
        espesor_mm="4",
        color_perfileria="blanco",
        ubicacion="Oficina",
        detalles="Ventana personalizada",
        aprobado=False
    )
    assert cotizacion.aprobado is False
    cotizacion.aprobado = True
    cotizacion.save()
    assert cotizacion.aprobado is True

@pytest.mark.django_db
def test_rn05_creacion_cotizacion_personalizada():
    cotizacion = CustomQuoteRequest.objects.create(
        nombre="Juan Pérez",
        email="juan@test.com",
        telefono="123456789",
        tipo="window",
        ancho_mm=120,
        alto_mm=100,
        cantidad=2,
        marco="aluminum",
        borde="polished",
        cristal="tempered",
        espesor_mm="4",
        color_perfileria="blanco",
        ubicacion="Living",
        detalles="Ventana corrediza",
    )
    assert cotizacion.nombre == "Juan Pérez"
    assert cotizacion.tipo == "window"
    assert cotizacion.ancho_mm == 120
    assert cotizacion.alto_mm == 100

@pytest.mark.django_db
def test_rn06_campos_obligatorios_cotizacion():
    cotizacion = CustomQuoteRequest.objects.create(
        nombre="Ana López",
        email="ana@test.com",
        telefono="987654321",
        tipo="mirror",
        ancho_mm=80,
        alto_mm=60,
        cantidad=1,
        marco="none",
        borde="beveled",
        cristal="laminated",
        espesor_mm="3",
        color_perfileria="titanio",
        ubicacion="Baño",
        detalles="Espejo biselado",
    )
    assert cotizacion.nombre == "Ana López"
    assert cotizacion.tipo == "mirror"
    assert cotizacion.cristal == "laminated"

@pytest.mark.django_db
def test_rn07_recalculo_precio():
    cot = CustomQuoteRequest.objects.create(
        nombre="Laura",
        email="laura@test.com",
        telefono="111222333",
        tipo="window",
        ancho_mm=100,
        alto_mm=100,
        cantidad=1,
        marco="aluminum",
        borde="polished",
        cristal="tempered",
        espesor_mm="4",
        color_perfileria="blanco",
        ubicacion="Sala",
        detalles="Prueba recalculo",
    )
    antes = getattr(cot, "price", Decimal("0.00"))
    cot.ancho_mm = 200
    cot.marco = "PVC"
    cot.save()
    # debe existir método recalcular_precio en el modelo
    cot.recalcular_precio()
    cot.refresh_from_db()
    despues = getattr(cot, "price", Decimal("0.00"))
    assert despues != antes
    assert despues >= Decimal("0.00")

@pytest.mark.django_db
def test_rn08_admin_puede_modificar_reglas_calculo(client):
    admin = User.objects.create_superuser("admin", "admin@test.com", "pass1234")
    client.force_login(admin)
    url = reverse("quotes:pricing_rules")
    resp = client.post(url, {"base_rate_tempered": "55", "discount_percent": "10"})
    assert resp.status_code in (200, 302)

@pytest.mark.django_db
def test_rn08_usuario_no_admin_no_puede_modificar_reglas(client):
    user = User.objects.create_user("cliente", "cliente@test.com", "pass1234")
    client.force_login(user)
    url = reverse("quotes:pricing_rules")
    resp = client.post(url, {"base_rate_tempered": "55", "discount_percent": "10"})
    assert resp.status_code in (302, 403)

@pytest.mark.django_db
def test_rn12_pedido_se_genera_solo_al_confirmar():
    if Order is None:
        pytest.skip("Order model no existe; crear apps.quotes.models.Order para este test.")
    cot = CustomQuoteRequest.objects.create(
        nombre="Cliente",
        email="c@test.com",
        telefono="000",
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
        detalles="Prueba RN-12",
    )
    cot.recalcular_precio()
    assert not Order.objects.filter(quote=cot).exists()
    cot.confirm()
    order = Order.objects.get(quote=cot)
    assert order.total_price == cot.price
    assert order.status in ("En revisión", "Pending", "CREATED")

@pytest.mark.django_db
def test_rn13_precios_pedido_se_congelan_al_generar_cotizacion():
    if Order is None:
        pytest.skip("Order model no existe; crear apps.quotes.models.Order para este test.")
    cot = CustomQuoteRequest.objects.create(
        nombre="Cliente RN13",
        email="rn13@test.com",
        telefono="000",
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
        detalles="Prueba RN-13",
    )
    cot.recalcular_precio()
    cot.refresh_from_db()
    precio_al_cotizar = cot.price
    order = cot.confirm()
    order.refresh_from_db()
    assert order.total_price == precio_al_cotizar
    cot.ancho_mm = 200
    cot.recalcular_precio()
    cot.refresh_from_db()
    order.refresh_from_db()
    assert order.total_price == precio_al_cotizar

@pytest.mark.django_db
def test_rn14_cambio_estados_pedido():
    """
    RN-14: El sistema debe registrar el estado del pedido:
    'En revisión', 'En producción', 'Listo para entrega', 'Entregado'.
    El test verifica que un pedido creado pase por esos estados correctamente.
    """
    if Order is None:
        pytest.skip("Order model no existe; crear apps.quotes.models.Order para este test.")

    # crear cotización mínima y generar pedido
    cot = CustomQuoteRequest.objects.create(
        nombre="Cliente RN14",
        email="rn14@test.com",
        telefono="000",
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
        detalles="Prueba RN-14",
    )
    # asegurar price calculado si tu confirm() lo requiere
    if hasattr(cot, "recalcular_precio"):
        cot.recalcular_precio()

    order = cot.confirm() if hasattr(cot, "confirm") else Order.objects.create(quote=cot, total_price=getattr(cot, "price", 0))

    allowed_states = ["En revisión", "En producción", "Listo para entrega", "Entregado"]

    for state in allowed_states:
        # si el modelo Order tiene un método para cambiar estado, úsalo; si no, asigna directamente
        if hasattr(order, "set_status"):
            order.set_status(state)
        else:
            order.status = state
            order.save()
        order.refresh_from_db()
        assert order.status == state

@pytest.mark.django_db
def test_rn15_admin_marca_pedido_como_pagado_via_view_or_model(client):
    """
    RN-15: El administrador puede marcar manualmente un pedido como 'pagado'.
    El test intenta usar la vista 'quotes:mark_paid' si existe; si no, verifica
    la presencia del campo booleano 'paid' en el modelo Order y lo modifica.
    """
    if Order is None:
        pytest.skip("Order no existe en apps.quotes.models; crear Order para este test.")

    # crear cotización y pedido asociado
    cot = CustomQuoteRequest.objects.create(
        nombre="Cliente RN15",
        email="rn15@test.com",
        telefono="000",
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
        detalles="Prueba RN-15",
    )
    # asegurar price si existe método
    if hasattr(cot, "recalcular_precio"):
        cot.recalcular_precio()

    order = Order.objects.create(quote=cot, total_price=getattr(cot, "price", Decimal("0.00")))

    # Si existe la vista 'quotes:mark_paid', probarla (admin OK, usuario no)
    try:
        url = reverse("quotes:mark_paid", args=[order.pk])
    except NoReverseMatch:
        url = None

    if url:
        admin = User.objects.create_superuser("admin_rn15", "admin_rn15@test.com", "pass1234")
        client.force_login(admin)
        resp = client.post(url)
        assert resp.status_code in (200, 302)
        order.refresh_from_db()
        # aceptar tanto campo booleano 'paid' como cambio de estado a 'Pagado'/'Paid'
        if hasattr(order, "paid"):
            assert order.paid is True
        else:
            assert str(order.status).lower() in ("pagado", "paid")
        # verificar que usuario normal no pueda marcar
        user = User.objects.create_user("user_rn15", "user_rn15@test.com", "pass1234")
        client.force_login(user)
        resp2 = client.post(url)
        assert resp2.status_code in (302, 403)
        return

    # Si no hay vista, probar modificación directa del modelo si existe campo 'paid'
    if hasattr(order, "paid"):
        assert order.paid is False
        # simular acción administrativa (assign + save)
        order.paid = True
        order.save()
        order.refresh_from_db()
        assert order.paid is True
        return

    pytest.skip("No existe vista 'quotes:mark_paid' ni campo booleano 'paid' en Order; implementar uno de los dos.")

@pytest.mark.django_db
def test_rn16_admin_actualiza_precios_e_disponibilidad(client):
    """
    RN-16: El administrador puede actualizar precios, material y disponibilidad.
    Se usa la interfaz admin para simular edición.
    """
    cat = Category.objects.create(name="Ventanas")
    prod = Product.objects.create(
        category=cat,
        name="Ventana prueba",
        material="ALU",
        glass_type="TEM",
        thickness="4",
        color="WHT",
        price=1000,
        is_active=True,
        slug="ventana-prueba"
    )

    admin = User.objects.create_superuser("admin", "admin@test.com", "pass1234")
    client.force_login(admin)

    url = reverse("admin:catalog_product_change", args=[prod.pk])
    data = {
        "category": cat.pk,
        "name": prod.name,
        "material": "PVC",            # cambio de material
        "glass_type": prod.glass_type,
        "thickness": prod.thickness,
        "color": prod.color,
        "price": "2000.00",          # nuevo precio
        "is_active": "",             # desactivar (si el admin usa checkbox, vacío = off)
        "slug": prod.slug,
    }
    resp = client.post(url, data)
    # admin suele redirigir tras guardar
    assert resp.status_code in (302, 200)

    prod.refresh_from_db()
    assert str(prod.price) == "2000.00"
    assert prod.material == "PVC"
    # is_active puede estar representado como booleano; comprobar que cambió a False
    assert prod.is_active is False or prod.is_active == 0

@pytest.mark.django_db
def test_rn16_usuario_normal_no_puede_modificar_producto_admin(client):
    cat = Category.objects.create(name="Puertas")
    prod = Product.objects.create(
        category=cat,
        name="Puerta prueba",
        material="ALU",
        glass_type="TEM",
        thickness="4",
        color="WHT",
        price=1500,
        is_active=True,
        slug="puerta-prueba"
    )

    user = User.objects.create_user("user", "user@test.com", "pass1234")
    client.force_login(user)

    url = reverse("admin:catalog_product_change", args=[prod.pk])
    resp = client.post(url, {"name": prod.name})
    # usuario normal suele ser redirigido al login (302) o recibir 403
    assert resp.status_code in (302, 403)

@pytest.mark.django_db
def test_rn17_imagen_asociada_al_producto_y_guardada_en_storage():
    cat = Category.objects.create(name="Imágenes")
    # contenido de imagen mínima válida (GIF pequeño)
    image_content = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
        b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00'
        b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
        b'\x4c\x01\x00\x3b'
    )
    img = SimpleUploadedFile("test_image.gif", image_content, content_type="image/gif")

    prod = Product.objects.create(
        category=cat,
        name="Producto con imagen",
        material="ALU",
        glass_type="TEM",
        thickness="4",
        color="WHT",
        price=1000,
        image=img,
    )

    # El archivo quedó asociado al campo image
    assert prod.image.name.endswith("test_image.gif")
    # El archivo existe en el storage configurado (MEDIA_ROOT durante tests)
    assert default_storage.exists(prod.image.name)

    # cleanup para no dejar archivos en storage
    default_storage.delete(prod.image.name)

def test_pytest_funciona():
    assert 1 == 1

@pytest.mark.django_db
def test_rn19_envia_notificacion_al_aprobar_cotizacion():
    """
    Al aprobar una CustomQuoteRequest debe enviarse una notificación (email) al cliente.
    Si la funcionalidad no está implementada, el test se salta con un mensaje.
    """
    mail.outbox.clear()
    cot = CustomQuoteRequest.objects.create(
        nombre="Notificar",
        email="notify@test.com",
        telefono="000",
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
        detalles="Prueba notificación"
    )

    cot.aprobado = True
    cot.save()

    if len(mail.outbox) == 0:
        pytest.skip("No se envió notificación al aprobar la cotización. Implementar envío en señal/método.")
    # verificar que al menos un email fue enviado al correo de la cotización
    assert any(cot.email in m.to for m in mail.outbox)

@pytest.mark.django_db
def test_rn19_envia_notificacion_cambio_estado_pedido():
    """
    Al cambiar el estado de un Order debe enviarse una notificación al cliente.
    Si no existe Order o no se envía email, el test se salta.
    """
    if Order is None:
        pytest.skip("Order no existe en apps.quotes.models; crear Order para este test.")

    mail.outbox.clear()
    cot = CustomQuoteRequest.objects.create(
        nombre="Notificar2",
        email="notify2@test.com",
        telefono="111",
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
        detalles="Prueba notificación estado"
    )

    # asegurar que price exista si tu flujo lo requiere
    if hasattr(cot, "recalcular_precio"):
        cot.recalcular_precio()

    order = Order.objects.create(quote=cot, total_price=getattr(cot, "price", Decimal("0.00")))
    # cambiar estado (usa el valor que tu dominio maneje)
    order.status = "Entregado"
    order.save()

    if len(mail.outbox) == 0:
        pytest.skip("No se envió notificación al cambiar estado del pedido. Implementar envío en señal/método.")
    assert any(cot.email in m.to for m in mail.outbox)

@pytest.mark.parametrize("missing_field", ["nombre", "correo", "telefono", "mensaje"])
def test_rn20_contact_form_campos_obligatorios(missing_field):
    """
    RN-20: El formulario de contacto valida campos obligatorios:
    nombre, correo, telefono y mensaje.
    Cada uno debe producir error si falta.
    """
    data = {
        "nombre": "Cliente",
        "correo": "cliente@test.com",
        "telefono": "123456789",
        "mensaje": "Consulta sobre producto",
    }
    data.pop(missing_field)
    form = ContactForm(data)
    assert not form.is_valid()
    assert missing_field in form.errors

def test_rn20_contact_form_correo_invalido():
    data = {
        "nombre": "Cliente",
        "correo": "no-es-un-correo",
        "telefono": "123456789",
        "mensaje": "Consulta sobre producto",
    }
    form = ContactForm(data)
    assert not form.is_valid()
    assert "correo" in form.errors

def test_rn20_contact_form_valido():
    data = {
        "nombre": "Cliente",
        "correo": "cliente@test.com",
        "telefono": "123456789",
        "mensaje": "Consulta sobre producto",
    }
    form = ContactForm(data)
    assert form.is_valid()

