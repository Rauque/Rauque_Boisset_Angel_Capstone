# payments/views.py
import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from apps.catalog.models import Product
from .flow_client import flow_post, flow_get, FlowError

logger = logging.getLogger(__name__)


def flow_pay_product(request, pk: int):
    """
    Crea un pago en Flow para 1 unidad de un producto
    y redirige al usuario a la URL de pago de Flow.
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # Solo aceptamos POST para evitar que alguien dispare pagos con GET
    if request.method != "POST":
        return redirect("catalog:product_detail", slug=product.slug)

    # Chequeo básico de configuración
    if not settings.FLOW_API_KEY or not settings.FLOW_SECRET_KEY:
        # Aquí, en settings.py, se están usando tus llaves:
        # FLOW_API_KEY = "3ACF739C-C523-45AA-A5B5-5E7D6L3BFC29"
        # FLOW_SECRET_KEY = "386473ac583e7d7ed49363983c451996dea9869a"
        return render(
            request,
            "payments/flow_result.html",
            {
                "title": "Configuración de Flow incompleta",
                "lead": "Revisa FLOW_API_KEY y FLOW_SECRET_KEY en settings/.env.",
                "status": None,
                "raw": None,
            },
        )

    commerce_order = f"product-{product.pk}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    subject = f"Compra {product.name}"
    amount = str(product.price)

    if request.user.is_authenticated and request.user.email:
        email = request.user.email
    else:
        # fallback razonable
        email = getattr(settings, "COTIZADOR_TO", "comervial.hr@gmail.com")

    params = {
        "commerceOrder": commerce_order,
        "subject": subject,
        "currency": "CLP",
        "amount": amount,
        "email": email,
        "urlConfirmation": settings.FLOW_CONFIRM_URL,
        "urlReturn": settings.FLOW_RETURN_URL,
    }

    try:
        # Llama a /payment/create en Flow usando la API key
        # (FLOW_API_KEY = "3ACF739C-C523-45AA-A5B5-5E7D6L3BFC29")
        # y firma con la secret key
        # (FLOW_SECRET_KEY = "386473ac583e7d7ed49363983c451996dea9869a")
        data = flow_post("/payment/create", params)
    except FlowError as e:
        logger.exception("Error al crear pago en Flow")
        return render(
            request,
            "payments/flow_result.html",
            {
                "title": "No se pudo iniciar el pago con Flow",
                "lead": str(e),
                "status": None,
                "raw": None,
            },
        )

    flow_url = data.get("url")
    token = data.get("token")

    if not flow_url or not token:
        return render(
            request,
            "payments/flow_result.html",
            {
                "title": "Respuesta inválida de Flow",
                "lead": "No se recibió 'url' o 'token' al crear el pago.",
                "status": None,
                "raw": json.dumps(data, indent=2, ensure_ascii=False),
            },
        )

    # Redirigimos al usuario a Flow
    redirect_url = f"{flow_url}?token={token}"
    return redirect(redirect_url)


@csrf_exempt
def flow_confirm(request):
    """
    URL de confirmación que llama Flow (server to server).
    Aquí deberías actualizar el estado de la orden en tu BD.
    """
    token = request.POST.get("token") or request.GET.get("token")
    if not token:
        return HttpResponse("missing token", status=400)

    try:
        data = flow_get("/payment/getStatus", {"token": token})
        logger.info("Flow confirm getStatus: %s", data)
        # TODO: aquí podrías buscar tu orden por commerceOrder y marcarla pagada
    except FlowError as e:
        logger.exception("Error en confirmación Flow: %s", e)
        return HttpResponse("error", status=500)

    return HttpResponse("OK")


@csrf_exempt
def flow_return(request):
    """
    URL donde Flow redirige al usuario una vez finalizado el pago.
    Flow puede llegar por GET o POST, así que leemos de ambos.
    """
    token = request.GET.get("token") or request.POST.get("token")
    if not token:
        return render(
            request,
            "payments/flow_result.html",
            {
                "title": "Pago Flow",
                "lead": "No se recibió el token de Flow en la URL de retorno.",
                "status": None,
                "raw": None,
            },
        )

    try:
        data = flow_get("/payment/getStatus", {"token": token})
        status = data.get("status") or data.get("status_description") or data.get("statusText")
        raw_json = json.dumps(data, indent=2, ensure_ascii=False)
    except FlowError as e:
        return render(
            request,
            "payments/flow_result.html",
            {
                "title": "Error al consultar estado del pago",
                "lead": str(e),
                "status": None,
                "raw": None,
            },
        )

    s = str(status).lower() if status is not None else ""
    if s in ("2", "paid", "paid_out", "pagado"):
        title = "Pago Flow aprobado"
        lead = "Tu pago fue aprobado correctamente."
    elif s in ("1", "pending", "pendiente"):
        title = "Pago Flow pendiente"
        lead = "Tu pago está pendiente de confirmación."
    elif s:
        title = "Pago Flow rechazado"
        lead = f"Estado devuelto por Flow: {status}"
    else:
        title = "Pago Flow"
        lead = "Flow devolvió la siguiente información de la transacción."

    return render(
        request,
        "payments/flow_result.html",
        {
            "title": title,
            "lead": lead,
            "status": status,
            "raw": raw_json,
        },
    )