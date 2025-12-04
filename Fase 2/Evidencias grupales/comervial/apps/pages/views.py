from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django import forms as dj_forms
from django.core.mail import EmailMessage
import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

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

    # Ocultar categoría y forzar valor “otros” (si existe en el form)
    if "categoria" in form.fields:
        form.fields["categoria"].initial = "otros"
        form.fields["categoria"].widget = dj_forms.HiddenInput()

    if request.method == "POST" and form.is_valid():
        obj = form.save()  # guarda en QuoteRequest

        # Destinatario: CONTACT_TO -> COTIZADOR_TO -> DEFAULT_FROM_EMAIL
        to = getattr(settings, "CONTACT_TO",
             getattr(settings, "COTIZADOR_TO", getattr(settings, "DEFAULT_FROM_EMAIL", None)))

        if to:
            # Email con Reply-To al correo del cliente
            subject = "Nuevo contacto (Comervial)"
            body = (
                f"Nombre: {obj.nombre}\n"
                f"Email: {obj.email}\n"
                f"Teléfono: {obj.telefono}\n"
                f"Categoría: {getattr(obj, 'categoria', '')}\n\n"
                f"Mensaje:\n{obj.mensaje}"
            )
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                to=[to],
                reply_to=[obj.email] if obj.email else None,
            )
            # No silenciamos errores: si falla, lo sabrás
            email.send(fail_silently=False)

        messages.success(request, "¡Gracias! Tu mensaje fue enviado correctamente.")
        return redirect("contacto")  # ← volvemos a /contacto mostrando el alert

    return render(request, "pages/contacto.html", {"form": form})


def mp_checkout(request):
    # Ejemplo: pref para “anticipo de cotización” de $10.000 CLP
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    back = f"{settings.SITE_URL}{reverse('mp_return')}"
    webhook = f"{settings.SITE_URL}{reverse('mp_webhook')}"

    preference_data = {
        "items": [{
            "title": "Anticipo de cotización Comervial",
            "quantity": 1,
            "currency_id": "CLP",
            "unit_price": 10000
        }],
        "back_urls": {
            "success": back,
            "pending": back,
            "failure": back,
        },
        "auto_return": "approved",
        "notification_url": webhook,  # webhook
        "metadata": {
            "origen": "checkout_pro_demo",
            # aquí puedes guardar ID de cotización/cliente
        }
    }

    pref = sdk.preference().create(preference_data)
    init_point = pref["response"].get("init_point") or pref["response"].get("sandbox_init_point")
    return HttpResponseRedirect(init_point)

def mp_return(request):
    # Mercado Pago te devuelve parámetros GET como collection_status, payment_id, etc.
    # Aquí puedes mostrar un “gracias” y/o consultar el pago para confirmar.
    status = request.GET.get("collection_status")
    payment_id = request.GET.get("payment_id")
    preference_id = request.GET.get("preference_id")
    html = f"<h1>Estado: {status}</h1><p>payment_id: {payment_id}</p><p>preference_id: {preference_id}</p>"
    return HttpResponse(html)

@csrf_exempt
def mp_webhook(request):
    # Notificación server-to-server: valida y actualiza tu orden
    # Ej: ?type=payment&id=<payment_id>
    type_ = request.GET.get("type") or request.POST.get("type")
    payment_id = request.GET.get("id") or request.POST.get("data.id")

    if type_ == "payment" and payment_id:
        sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
        payment = sdk.payment().get(payment_id)
        # payment["response"]["status"] -> approved, pending, rejected, etc.
        # TODO: marcar pedido/cotización como PAGADO si status == "approved"
        # TODO: enviar emails de confirmación al cliente y a ti
        return JsonResponse({"ok": True})

    return JsonResponse({"ok": False})