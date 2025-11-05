from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django import forms as dj_forms

from apps.quotes.forms import ContactForm  # alias de QuoteRequestForm

def index(request):
    return render(request, "pages/index.html")

def barandas(request):
    return render(request, "pages/barandas.html")

def muebles(request):
    return render(request, "pages/muebles.html")

def shower_door(request):
    return render(request, "pages/shower_door.html")

def mamparas(request):
    return render(request, "pages/mamparas.html")

def reposicion_cristales(request):
    return render(request, "pages/reposicion_cristales.html")

def corredera(request):       return render(request, "pages/ventanas/corredera.html")
def abatible(request):        return render(request, "pages/ventanas/abatible.html")
def oscilobatiente(request):  return render(request, "pages/ventanas/oscilobatiente.html")
def proyectante(request):     return render(request, "pages/ventanas/proyectante.html")
def fija(request):            return render(request, "pages/ventanas/fija.html")
def bow_window(request):      return render(request, "pages/ventanas/bow_window.html")
def medio_punto(request):     return render(request, "pages/ventanas/medio_punto.html")

def puertas_abatibles(request):
    return render(request, "pages/puertas/abatibles.html")

def puertas_correderas(request):
    return render(request, "pages/puertas/correderas.html")

def puertas_elevadoras(request):
    return render(request, "pages/puertas/elevadoras.html")

def puertas_templado(request):
    return render(request, "pages/puertas/templado.html")

def contacto(request):
    form = ContactForm(request.POST or None)

    # Ocultar categoría y forzar valor “otros”
    if "categoria" in form.fields:
        form.fields["categoria"].initial = "otros"
        form.fields["categoria"].widget = dj_forms.HiddenInput()

    if request.method == "POST" and form.is_valid():
        obj = form.save()

        # destinatario: CONTACT_TO -> COTIZADOR_TO -> DEFAULT_FROM_EMAIL
        to = getattr(settings, "CONTACT_TO",
             getattr(settings, "COTIZADOR_TO", getattr(settings, "DEFAULT_FROM_EMAIL", None)))
        if to:
            try:
                send_mail(
                    "Nuevo contacto (Comervial)",
                    f"Nombre: {obj.nombre}\nEmail: {obj.email}\nTeléfono: {obj.telefono}\n\nMensaje:\n{obj.mensaje}",
                    getattr(settings, "DEFAULT_FROM_EMAIL", obj.email),
                    [to],
                    fail_silently=True,
                )
            except Exception:
                pass

        messages.success(request, "¡Gracias! Te contactaremos pronto.")
        return redirect("quotes:cotizador_ok")

    return render(request, "pages/contacto.html", {"form": form})