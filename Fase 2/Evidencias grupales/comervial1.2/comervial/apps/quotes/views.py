# apps/quotes/views.py
import io
import json
from decimal import Decimal
from datetime import date

from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.http import (
    HttpResponse,
    FileResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

from .forms import QuoteRequestForm, CustomQuoteRequestForm
from .pricing import PRODUCT_CATALOG, calcular_item_catalogo
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet


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
    if request.method == "GET":
        return render(request, "quotes/cotizador_personalizado.html")

    # Qué acción quiere el usuario: pdf o email
    mode = request.POST.get("mode", "pdf")  # por defecto: pdf

    # Datos de la cotización
    payload = request.POST.get("payload")
    if not payload:
        return HttpResponseBadRequest("Faltan datos de la cotización.")

    data = json.loads(payload)
    cliente = data.get("cliente", {})
    raw_items = data.get("items", [])

    # ===== Cálculo de ítems y totales (igual que antes) =====
    items = []
    subtotal = 0
    for raw in raw_items:
        item = calcular_item_catalogo(raw)
        items.append(item)
        subtotal += item["subtotal"]

    iva = round(subtotal * 0.19)
    total = subtotal + iva

    # ===== Generar PDF una sola vez =====
    buffer = _generate_catalog_pdf(cliente, items, subtotal, iva, total)
    pdf_bytes = buffer.getvalue()

    # Datos del cliente para el mail
    nombre_cliente = cliente.get("nombre") or cliente.get("name") or ""
    email_cliente = cliente.get("email") or ""
    telefono = cliente.get("telefono") or cliente.get("phone") or ""

    # ===== Si el modo es EMAIL: enviar correo y mostrar mensaje =====
    if mode == "email":
        subject = "Cotización personalizada Comervial"
        body = (
            f"Hola {nombre_cliente or 'cliente'},\n\n"
            "Adjuntamos la cotización personalizada que solicitaste en Comervial.\n\n"
            f"Total (IVA incluido): ${total:,.0f}\n\n"
            "Datos de contacto enviados:\n"
            f"- Nombre: {nombre_cliente}\n"
            f"- Email: {email_cliente}\n"
            f"- Teléfono: {telefono}\n\n"
            "Saludos,\n"
            "Comervial Vidriería"
        )

        destinatarios = []

        # correo empresa (define COTIZADOR_TO en settings.py)
        if getattr(settings, "COTIZADOR_TO", None):
            destinatarios.append(settings.COTIZADOR_TO)

        # correo cliente
        if email_cliente:
            destinatarios.append(email_cliente)

        if destinatarios:
            email = EmailMessage(
                subject,
                body,
                getattr(settings, "DEFAULT_FROM_EMAIL", None),
                destinatarios,
            )
            email.attach("cotizacion_comervial.pdf", pdf_bytes, "application/pdf")
            email.send(fail_silently=not settings.DEBUG)

        # Aquí decides qué hacer después de enviar el correo:
        # 1) Volver al cotizador con un mensaje
        # 2) Ir a una página de "gracias"
        # Si ya tienes 'cotizador_ok', podemos usar eso:
        from django.shortcuts import redirect
        return redirect("quotes:cotizador_ok")

    # ===== Si el modo es PDF: descargar PDF como antes =====
    buffer.seek(0)
    response = FileResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename=\"cotizacion_comervial.pdf\"'
    return response

def _generate_catalog_pdf(cliente, items, subtotal, iva, total):
    """
    Genera el PDF de cotización con texto de descripción más legible
    y con salto de línea automático.
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # Estilos básicos
    style_normal = styles["Normal"]
    style_normal.fontSize = 9
    style_normal.leading = 11

    style_title = styles["Heading2"]
    style_title.alignment = 1  # centrado

    story: list = []

    # --- Encabezado empresa ---
    story.append(Paragraph("Elba Rosa Ulloa Cáceres", style_normal))
    story.append(Paragraph("Comercialización de vidrios y aluminio", style_normal))
    story.append(Paragraph("Y servicio de instalaciones, limpieza", style_normal))
    story.append(Paragraph("Aseo y Suministro.", style_normal))
    story.append(Paragraph("El Lingue 8358 - Villa la Rotonda, La Florida, Santiago", style_normal))
    story.append(Spacer(1, 6))

    hoy_str = date.today().strftime("%d/%m/%Y")
    story.append(Paragraph(f"Fecha: {hoy_str}", style_normal))
    story.append(Spacer(1, 12))

    # Título de la cotización
    story.append(Paragraph("Cotización de suministros y servicios", style_title))
    story.append(Spacer(1, 18))

    # --- Datos del cliente ---
    if cliente:
        if cliente.get("nombre"):
            story.append(Paragraph(f"Cliente: {cliente['nombre']}", style_normal))
        if cliente.get("email"):
            story.append(Paragraph(f"Email: {cliente['email']}", style_normal))
        if cliente.get("telefono"):
            story.append(Paragraph(f"Teléfono: {cliente['telefono']}", style_normal))
        story.append(Spacer(1, 12))

    # --- Tabla de ítems ---
    data = [["Cant", "Descripción", "Precio unidad", "Bruto"]]

    for item in items:
        # Armamos una descripción más corta y ordenada
        # Ej: "Ventanas PVC Europeo · CORREDERA TERMOPANEL (150 x 180 cm, 1.80 m²)"
        desc_text = (
            f"{item['categoria']} · {item['tipo']} "
            f"({item['ancho_cm']} x {item['alto_cm']} cm, {item['m2']:.2f} m²)"
        )

        desc_paragraph = Paragraph(desc_text, style_normal)

        data.append(
            [
                str(item["cantidad"]),
                desc_paragraph,
                f"${item['precioUnitario']:,.0f}".replace(",", "."),
                f"${item['subtotal']:,.0f}".replace(",", "."),
            ]
        )

    # Anchos de columna pensados para que la descripción pueda quebrar en 2–3 líneas
    table = Table(
        data,
        colWidths=[20 * mm, 95 * mm, 30 * mm, 30 * mm],
        repeatRows=1,  # encabezado en cada página si se pasa de una hoja
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 1), (0, -1), "CENTER"),  # Cantidad
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),   # precios
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 18))

    # --- Resumen de totales ---
    resumen_data = [
        ["Neto", f"${subtotal:,.0f}".replace(",", ".")],
        ["IVA 19%", f"${iva:,.0f}".replace(",", ".")],
        ["Total", f"${total:,.0f}".replace(",", ".")],
    ]

    resumen_table = Table(resumen_data, colWidths=[40 * mm, 30 * mm])
    resumen_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    story.append(resumen_table)

    # Construye el PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def cotizador_ok(request):
    return render(request, "quotes/gracias.html")