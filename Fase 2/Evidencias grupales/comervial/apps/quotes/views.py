# apps/quotes/views.py
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QuoteRequestForm, CustomQuoteRequestForm
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden

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
