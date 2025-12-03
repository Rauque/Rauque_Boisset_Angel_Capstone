# payments/views.py
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from apps.catalog.models import Product
from .flow_client import flow_post, flow_get, FlowError
from .models import FlowOrder

logger = logging.getLogger(__name__)


@login_required
def flow_pay_product(request, pk: int):
    """
    Crea un pago en Flow para 1 unidad de un producto
    y redirige al usuario a la URL de pago de Flow.
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)

    if request.method != "POST":
        return redirect("catalog:product_detail", slug=product.slug)

    if not settings.FLOW_API_KEY or not settings.FLOW_SECRET_KEY:
        return render(
            request,
            "payments/flow_result.html",
            {
                "title": "Configuración de Flow incompleta",
                "lead": "Revisa FLOW_API_KEY y FLOW_SECRET_KEY en settings/.env.",
                "status": None,
                "order": None,
                "raw": None,
            },
        )

    commerce_order = f"product-{product.pk}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    subject = f"Compra {product.name}"
    amount = str(product.price)

    email = request.user.email or getattr(
        settings, "COTIZADOR_TO", "comervial.hr@gmail.com"
    )

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
                "order": None,
                "raw": None,
            },
        )

    flow_url = data.get("url")
    token = data.get("token")

    # Registramos la compra asociada al usuario
    FlowOrder.objects.create(
        user=request.user,
        product=product,
        quantity=1,
        amount=product.price,
        commerce_order=commerce_order,
        token=token,
        status="pending",
    )

    if not flow_url or not token:
        return render(
            request,
            "payments/flow_result.html",
            {
                "title": "Respuesta inválida de Flow",
                "lead": "No se recibió 'url' o 'token' al crear el pago.",
                "status": None,
                "order": None,
                "raw": json.dumps(data, indent=2, ensure_ascii=False),
            },
        )

    return redirect(f"{flow_url}?token={token}")


@csrf_exempt
def flow_confirm(request):
    """
    Confirmación server-to-server desde Flow.
    """
    token = request.POST.get("token") or request.GET.get("token")
    if not token:
        return HttpResponse("missing token", status=400)

    try:
        data = flow_get("/payment/getStatus", {"token": token})
        logger.info("Flow confirm getStatus: %s", data)
    except FlowError as e:
        logger.exception("Error en confirmación Flow: %s", e)
        return HttpResponse("error", status=500)

    commerce_order = data.get("commerceOrder")
    flow_order_id = data.get("flowOrder")
    status_code = str(data.get("status"))

    try:
        order = FlowOrder.objects.get(commerce_order=commerce_order)
    except FlowOrder.DoesNotExist:
        logger.error("No existe FlowOrder con commerce_order=%s", commerce_order)
        return HttpResponse("ok")

    order.flow_order = flow_order_id
    order.raw_response = data

    if status_code == "2":
        order.status = "paid"
    elif status_code == "1":
        order.status = "pending"
    else:
        order.status = "failed"

    order.save()
    return HttpResponse("OK")


@csrf_exempt
def flow_return(request):
    token = request.GET.get("token") or request.POST.get("token")
    if not token:
        return render(
            request,
            "payments/flow_result.html",
            {
                "title": "Pago Flow",
                "lead": "No se recibió el token de Flow en la URL de retorno.",
                "status": None,
                "order": None,
                "raw": None,
            },
        )

    order = None
    raw_json = None
    status = None

    try:
        data = flow_get("/payment/getStatus", {"token": token})
        status = data.get("status")
        raw_json = json.dumps(data, indent=2, ensure_ascii=False)

        commerce_order = data.get("commerceOrder")
        flow_order_id = data.get("flowOrder")

        try:
            order = FlowOrder.objects.get(commerce_order=commerce_order)

            # RE-LOGIN: si la orden tiene usuario y este request viene anónimo,
            # volvemos a autenticar al usuario de la compra.
            if order.user and not request.user.is_authenticated:
                login(request, order.user)
                request.user = order.user

            # Actualizamos datos de Flow
            order.flow_order = flow_order_id
            order.raw_response = data

            status_code = str(status)
            if status_code == "2":
                order.status = "paid"
            elif status_code == "1":
                order.status = "pending"
            else:
                order.status = "failed"

            order.save()
        except FlowOrder.DoesNotExist:
            logger.error(
                "No existe FlowOrder con commerce_order=%s (return)", commerce_order
            )

    except FlowError as e:
        return render(
            request,
            "payments/flow_result.html",
            {
                "title": "Error al consultar estado del pago",
                "lead": str(e),
                "status": None,
                "order": None,
                "raw": None,
            },
        )

    s = str(status).lower() if status is not None else ""
    if s == "2":
        title = "Pago Flow aprobado"
        lead = "Tu pago fue aprobado correctamente."
    elif s == "1":
        title = "Pago Flow pendiente"
        lead = "Tu pago está pendiente de confirmación."
    elif s:
        title = "Pago Flow rechazado"
        lead = f"Estado devuelto por Flow: {status}"
    else:
        title = "Pago Flow"
        lead = "Flow devolvió la información de la transacción."

    return render(
        request,
        "payments/flow_result.html",
        {
            "title": title,
            "lead": lead,
            "status": status,
            "order": order,
            "raw": raw_json,
        },
    )
