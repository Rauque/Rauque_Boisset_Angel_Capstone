# === Catálogo de productos para el nuevo cotizador ===

PRODUCT_CATALOG = {
    "Ventanas PVC Europeo": {
        "CORREDERA TERMOPANEL": 180000,
        "PROYECTANTE TERMOPANEL": 215000,
        "PUERTA TERMOPANEL": 240000,
    },
    "Ventanas PVC Americano": {
        "CORREDERA CRISTAL MONOLITICO": 75000,
        "PROYECTANTE CRISTAL MONOLITICO": 89000,
    },
    "Ventanas Aluminio": {
        "ALUMINIO SOLO CRISTAL": 80000,
        "ALUMINIO PROYECTANTE TERMOPANEL": 135000,
        "PUERTAS ALUMINIO": 130000,
    },
    "Cristales": {
        "CRISTAL 3MM": 15000,
        "CRISTAL 4MM": 19000,
        "CRISTAL 5MM": 22000,
        "CRISTAL 6MM": 24000,
        "CRISTAL 8MM": 45000,
        "CRISTAL 10MM": 48000,
        "CRISTAL LAMINADO 6MM": 35000,
        "CRISTAL LAMINADO 8MM": 42000,
        "CRISTAL LAMINADO 10MM": 68000,
        "CRISTAL TEMPLADO 5MM": 80000,
        "CRISTAL TEMPLADO 8MM": 95000,
        "CRISTAL TEMPLADO 10MM": 115000,
    },
    "Espejos": {
        "ESPEJO 3MM": 50000,
        "ESPEJO 4MM": 60000,
        "ESPEJO 5MM": 65000,
    },
}


def calcular_item_catalogo(raw_item: dict) -> dict:
    """
    raw_item:
      {
        "categoria": str,
        "tipo": str,
        "ancho_cm": number,
        "alto_cm": number,
        "cantidad": number
      }
    Devuelve el mismo dict + m2, precioUnitario, subtotal.
    """
    categoria = raw_item["categoria"]
    tipo = raw_item["tipo"]
    ancho_cm = float(raw_item["ancho_cm"])
    alto_cm = float(raw_item["alto_cm"])
    cantidad = int(raw_item.get("cantidad", 1))

    precio_unit = PRODUCT_CATALOG.get(categoria, {}).get(tipo)
    if precio_unit is None:
        raise ValueError(f"Tipo '{tipo}' no encontrado en categoría '{categoria}'")

    m2 = (ancho_cm / 100.0) * (alto_cm / 100.0)
    subtotal = round(precio_unit * m2 * cantidad)

    return {
        **raw_item,
        "m2": m2,
        "precioUnitario": precio_unit,
        "cantidad": cantidad,
        "subtotal": subtotal,
    }
