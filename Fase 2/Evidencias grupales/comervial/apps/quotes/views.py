# apps/quotes/views.py
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QuoteRequestForm, CustomQuoteRequestForm

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

def cotizador_personalizado(request):
    if request.method == "POST":
        form = CustomQuoteRequestForm(request.POST)
        if form.is_valid():
            obj = form.save()
            try:
                send_mail(
                    "Nueva cotización (Personalizada)",
                    (
                        f"Nombre: {obj.nombre}\n"
                        f"Email: {obj.email}\n"
                        f"Teléfono: {obj.telefono}\n"
                        f"Tipo: {obj.tipo}\n"
                        f"Dimensiones: {obj.ancho_mm} x {obj.alto_mm} mm\n"
                        f"Ubicación: {obj.ubicacion}\n\n"
                        f"Detalles:\n{obj.detalles}\n"
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.COTIZADOR_TO],
                    fail_silently=not settings.DEBUG,
                )
            except Exception:
                pass
            messages.success(request, "¡Gracias! Tu solicitud personalizada fue enviada.")
            return redirect("quotes:cotizador_ok")
    else:
        form = CustomQuoteRequestForm()
    return render(request, "quotes/cotizador_personalizado.html", {"form": form})

def cotizador_ok(request):
    return render(request, "quotes/gracias.html")
