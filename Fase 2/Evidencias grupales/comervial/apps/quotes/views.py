from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import QuoteRequestForm, CustomQuoteRequestForm

def cotizador(request):
    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            obj = form.save()
            subject = "Nueva cotización (Cotizador)"
            body = f"""Nombre: {obj.nombre}
Email: {obj.email}
Teléfono: {obj.telefono}
Categoría: {obj.categoria}

Mensaje:
{obj.mensaje}
"""
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.COTIZADOR_TO])
            return redirect("cotizador_ok")
    else:
        form = QuoteRequestForm()
    return render(request, "quotes/cotizador.html", {"form": form})

def cotizador_personalizado(request):
    if request.method == "POST":
        form = CustomQuoteRequestForm(request.POST)
        if form.is_valid():
            obj = form.save()
            subject = "Nueva cotización (Personalizada)"
            body = f"""Nombre: {obj.nombre}
Email: {obj.email}
Teléfono: {obj.telefono}
Tipo: {obj.tipo}
Dimensiones: {obj.ancho_mm} x {obj.alto_mm} mm
Ubicación: {obj.ubicacion}

Detalles:
{obj.detalles}
"""
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.COTIZADOR_TO])
            return redirect("cotizador_ok")
    else:
        form = CustomQuoteRequestForm()
    return render(request, "quotes/cotizador_personalizado.html", {"form": form})

def cotizador_ok(request):
    return render(request, "quotes/gracias.html")
