# apps/quotes/views.py
import io
import json
from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QuoteRequestForm, CustomQuoteRequestForm
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden
from .pricing import PRODUCT_CATALOG, calcular_item_catalogo
from reportlab.lib.units import mm  
@user_passes_test(lambda u: u.is_superuser)
def pricing_rules(request):
    """
    Vista mínima para que solo superusers modifiquen reglas de cálculo.
    Implementa POST para guardar reglas reales si las tienes.
    """
    if request.method == "POST":
        # procesar datos recibidos y almacenarlos en tu modelo/setting
        # ejemplo mínimo: redirigir a la misma página
        return redirect("quotes:pricing_rules")
    # GET puede devolver una plantilla o 200 vacío
    return render(request, "quotes/pricing_rules.html", {})

def cotizador(request):
    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            obj = form.save()
            # Envío de correo: no rompas la vista si hay error SMTP
            try:
                send_mail(
                    "Nueva cotización (Cotizador)",
                    (
                        f"Nombre: {obj.nombre}\n"
                        f"Email: {obj.email}\n"
                        f"Teléfono: {obj.telefono}\n"
                        f"Categoría: {obj.categoria}\n\n"
                        f"Mensaje:\n{obj.mensaje}\n"
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.COTIZADOR_TO],
                    fail_silently=not settings.DEBUG,  # en DEBUG: muestra error si falla
                )
            except Exception:
                # Si algo sale mal en prod, no caigas
                pass
            messages.success(request, "¡Gracias! Tu solicitud fue enviada.")
            return redirect("quotes:cotizador_ok")
    else:
        form = QuoteRequestForm()
    return render(request, "quotes/cotizador.html", {"form": form})

@require_http_methods(["GET", "POST"])
def cotizador_personalizado(request):
    """
    GET  -> muestra el cotizador tipo Figma (HTML + JS).
    POST -> recibe JSON (payload) y devuelve un PDF de cotización.
    """
    if request.method == "GET":
        return render(request, "quotes/cotizador_personalizado.html")

    # POST -> generar PDF
    payload = request.POST.get("payload")
    if not payload:
        return HttpResponseBadRequest("Faltan datos de la cotización.")

    data = json.loads(payload)
    cliente = data.get("cliente", {})
    raw_items = data.get("items", [])

    items = []
    subtotal = 0
    for raw in raw_items:
        item = calcular_item_catalogo(raw)
        items.append(item)
        subtotal += item["subtotal"]

    iva = round(subtotal * 0.19)
    total = subtotal + iva

    buffer = _generate_catalog_pdf(cliente, items, subtotal, iva, total)
    response = FileResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="cotizacion_comervial.pdf"'
    return response

def _generate_catalog_pdf(cliente, items, subtotal, iva, total):
    """
    PDF estilo planilla: Cant / Descripción / Precio unidad / Bruto + resumen.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Encabezado
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20*mm, height - 20*mm, "Elba Rosa Ulloa Cáceres")
    c.setFont("Helvetica", 9)
    c.drawString(20*mm, height - 25*mm, "Comercialización de vidrios y aluminio")
    c.drawString(20*mm, height - 30*mm, "Y servicio de instalaciones, limpieza")
    c.drawString(20*mm, height - 35*mm, "Aseo y Suministro.")
    c.drawString(20*mm, height - 40*mm, "El Lingue 8358 - Villa la Rotonda, La Florida, Santiago")

    fecha_str = timezone.localdate().strftime("%d/%m/%Y")
    c.drawRightString(width - 20*mm, height - 20*mm, f"Fecha: {fecha_str}")

    # Título
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 55*mm, "Cotización de suministros y servicios")

    # Datos cliente
    y = height - 70*mm
    c.setFont("Helvetica", 9)
    if cliente.get("nombre"):
        c.drawString(20*mm, y, f"Cliente: {cliente.get('nombre')}")
        y -= 5*mm
    if cliente.get("email"):
        c.drawString(20*mm, y, f"Email: {cliente.get('email')}")
        y -= 5*mm
    if cliente.get("telefono"):
        c.drawString(20*mm, y, f"Teléfono: {cliente.get('telefono')}")
        y -= 8*mm

    # Cabecera tabla
    c.setFont("Helvetica-Bold", 9)
    y -= 5*mm
    c.drawString(20*mm, y, "Cant")
    c.drawString(35*mm, y, "Descripción")
    c.drawRightString(150*mm, y, "Precio unidad")
    c.drawRightString(190*mm, y, "Bruto")
    y -= 3*mm
    c.line(20*mm, y, 190*mm, y)
    y -= 4*mm

    # Filas
    c.setFont("Helvetica", 9)
    for item in items:
        if y < 40*mm:
            c.showPage()
            y = height - 30*mm

        desc = (
            f"{item['categoria']} - {item['tipo']} "
            f"({item['ancho_cm']} x {item['alto_cm']} cm, {item['m2']:.2f} m²)"
        )
        c.drawString(20*mm, y, str(item["cantidad"]))
        c.drawString(35*mm, y, desc[:80])  # recorte por si es muy largo
        c.drawRightString(150*mm, y, f"${int(item['precioUnitario']):,}".replace(",", "."))
        c.drawRightString(190*mm, y, f"${int(item['subtotal']):,}".replace(",", "."))
        y -= 6*mm

    # Línea final
    y -= 4*mm
    c.line(20*mm, y, 190*mm, y)

    # Resumen
    y -= 15*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(150*mm, y, "Neto")
    c.drawRightString(190*mm, y, f"${int(subtotal):,}".replace(",", "."))
    y -= 6*mm
    c.setFont("Helvetica", 10)
    c.drawRightString(150*mm, y, "IVA 19%")
    c.drawRightString(190*mm, y, f"${int(iva):,}".replace(",", "."))
    y -= 6*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(150*mm, y, "Total")
    c.drawRightString(190*mm, y, f"${int(total):,}".replace(",", "."))

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
