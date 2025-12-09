# comervial/payments/flow_client.py
import hashlib
import hmac
from urllib.parse import urlencode

import requests
from django.conf import settings


class FlowError(Exception):
    pass


def _signed_params(params: dict) -> dict:
    """
    Añade apiKey y firma s a los parámetros.
    - Ordenar por nombre de parámetro (ascendente)
    - Concatenar key + value
    - HMAC-SHA256 con secretKey
    """
    if not settings.FLOW_API_KEY or not settings.FLOW_SECRET_KEY:
        raise FlowError("Faltan FLOW_API_KEY / FLOW_SECRET_KEY en settings/env")

    payload = params.copy()
    payload["apiKey"] = settings.FLOW_API_KEY

    sorted_items = sorted(payload.items(), key=lambda kv: kv[0])
    to_sign = "".join(f"{k}{v}" for k, v in sorted_items)

    signature = hmac.new(
        settings.FLOW_SECRET_KEY.encode("utf-8"),
        to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    payload["s"] = signature
    return payload


def flow_post(path: str, params: dict) -> dict:
    """
    Llama a la API de Flow vía POST (x-www-form-urlencoded).
    Ejemplo: /payment/create
    """
    payload = _signed_params(params)
    body = urlencode(payload)

    url = settings.FLOW_API_URL.rstrip("/") + path
    resp = requests.post(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    if resp.status_code != 200:
        raise FlowError(f"HTTP {resp.status_code}: {resp.text}")

    data = resp.json()
    if isinstance(data, dict) and data.get("code") not in (None, 0):
        raise FlowError(f"Flow error {data.get('code')}: {data.get('message')}")
    return data


def flow_get(path: str, params: dict) -> dict:
    """
    Llama a la API de Flow vía GET.
    Ejemplo: /payment/getStatus
    """
    payload = _signed_params(params)
    qs = urlencode(payload)

    url = settings.FLOW_API_URL.rstrip("/") + path + "?" + qs
    resp = requests.get(url, timeout=10)

    if resp.status_code != 200:
        raise FlowError(f"HTTP {resp.status_code}: {resp.text}")

    data = resp.json()
    if isinstance(data, dict) and data.get("code") not in (None, 0):
        raise FlowError(f"Flow error {data.get('code')}: {data.get('message')}")
    return data
