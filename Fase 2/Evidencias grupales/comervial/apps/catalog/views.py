# apps/catalog/views.py
import json
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from .forms import ProductForm
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import (
    Product, Category,
    MATERIAL_CHOICES, GLASS_CHOICES, THICKNESS_CHOICES, COLOR_CHOICES
)

def product_list(request):
    qs = Product.objects.filter(is_active=True)

    # Filtros por querystring
    material  = request.GET.get("material")  or ""
    glass     = request.GET.get("cristal")   or ""
    thickness = request.GET.get("espesor")   or ""
    color     = request.GET.get("color")     or ""
    category  = request.GET.get("categoria") or ""

    if material:  qs = qs.filter(material=material)
    if glass:     qs = qs.filter(glass_type=glass)
    if thickness: qs = qs.filter(thickness=thickness)
    if color:     qs = qs.filter(color=color)
    if category:  qs = qs.filter(category__slug=category)

    paginator = Paginator(qs.select_related("category"), 12)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    ctx = {
        "products": products,
        "categories": Category.objects.all(),
        "MATERIAL_CHOICES": MATERIAL_CHOICES,
        "GLASS_CHOICES": GLASS_CHOICES,
        "THICKNESS_CHOICES": THICKNESS_CHOICES,
        "COLOR_CHOICES": COLOR_CHOICES,
        "current": {
            "material": material, "cristal": glass, "espesor": thickness,
            "color": color, "categoria": category
        },
    }
    return render(request, "catalog/list.html", ctx)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "catalog/detail.html", {
        "product": product,
        "MP_PUBLIC_KEY": settings.MP_PUBLIC_KEY,
        })
# Funciones de administración (solo para superusuarios)


def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_superuser)
def manage_products(request):
    qs = Product.objects.all().select_related("category").order_by("-created_at")
    return render(request, "catalog/manage_list.html", {"products": qs})

@login_required
@user_passes_test(is_superuser)
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto creado correctamente.")
        return redirect("catalog:catalog_manage")
    return render(request, "catalog/product_form.html", {"form": form, "title": "Nuevo producto"})

@login_required
@user_passes_test(is_superuser)
def product_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado.")
        return redirect("catalog:catalog_manage")
    return render(request, "catalog/product_form.html", {"form": form, "title": "Editar producto"})

@login_required
@user_passes_test(is_superuser)
def product_delete(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Producto eliminado.")
        return redirect("catalog:catalog_manage")
    return render(request, "catalog/product_delete_confirm.html", {"product": obj})


def _price_to_float(value):
    # Asegura float seguro para Mercado Pago
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except Exception:
        return 0.0

def mp_pref(request, pk: int):
    """
    Crea una preferencia de MP para 1 unidad del producto (modo test).
    Retorna { id: '<preference_id>' }.
    """
    try:
        import mercadopago
    except ImportError:
        return JsonResponse({"error": "SDK no instalado"}, status=500)

    product = Product.objects.filter(pk=pk, is_active=True).first()
    if not product:
        return JsonResponse({"error": "Producto no encontrado"}, status=404)

    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    preference_data = {
        "items": [{
            "title": product.name,
            "quantity": 1,
            "unit_price": _price_to_float(product.price),
            "currency_id": "CLP",
        }],
        "back_urls": {
            "success": settings.MP_SUCCESS_URL,
            "failure": settings.MP_FAILURE_URL,
            "pending": settings.MP_PENDING_URL,
        },
        "auto_return": "approved",
        "binary_mode": True,  # en test simplifica el flujo "aprobado/rechazado"
        "notification_url": settings.MP_WEBHOOK_URL,
        # Opcional: referencia para correlacionar luego en el webhook
        "external_reference": f"product:{product.pk}",
    }

    pref = sdk.preference().create(preference_data)
    # Estructura esperada: {"response": {"id": "..."} , "status": 201, ...}
    pref_id = pref.get("response", {}).get("id")
    if not pref_id:
        return JsonResponse({"error": "No se pudo crear preferencia", "raw": pref}, status=500)

    return JsonResponse({"id": pref_id})

def mp_success(request):
    # Aquí podrías leer ?payment_id=&status=&external_reference=...
    return render(request, "catalog/mp_result.html", {
        "title": "Pago aprobado",
        "lead": "Tu pago fue aprobado (TEST). Te enviaremos la confirmación por correo."
    })

def mp_failure(request):
    return render(request, "catalog/mp_result.html", {
        "title": "Pago rechazado",
        "lead": "El pago no fue procesado. Puedes intentar nuevamente."
    })

def mp_pending(request):
    return render(request, "catalog/mp_result.html", {
        "title": "Pago pendiente",
        "lead": "Tu pago quedó pendiente. Te avisaremos cuando se acredite."
    })

@csrf_exempt
def mp_webhook(request):
    """
    Webhook para recibir notificaciones (TEST).
    Por ahora solo responde 200; en real podrías consultar el pago y
    marcar la orden como pagada.
    """
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    # *** Aquí podrías guardar el payload en DB para debugging ***
    # print("MP webhook:", payload)

    return HttpResponse("ok", status=200)