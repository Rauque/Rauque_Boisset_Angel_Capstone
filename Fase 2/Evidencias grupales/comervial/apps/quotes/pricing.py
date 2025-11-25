# === Catálogo de productos para el nuevo cotizador ===

PRODUCT_CATALOG = {
    "Ventanas PVC Europeo": {
        "MT2 PVC CORREDERA TERMOPANEL": 180000,
        "MT2 PVC PROYECTANTE TERMOPANEL": 215000,
        "MT2 PVC PUERTA TERMOPANEL": 240000,
    },
    "Ventanas PVC Americano": {
        "MT2 PVC CORREDERA CRISTAL MONOLITICO": 75000,
        "MT2 PVC PROYECTANTE CRISTAL MONOLITICO": 89000,
    },
    "Ventanas Aluminio": {
        "MT2 ALUMINIO SOLO CRISTAL": 80000,
        "MT2 ALUMINIO PROYECTANTE TERMOPANEL": 135000,
        "MT2 PUERTAS ALUMINIO": 130000,
    },
    "Cristales": {
        "CRISTAL 3MM MT2": 15000,
        "CRISTAL 4MM MT2": 19000,
        "CRISTAL 5MM MT2": 22000,
        "CRISTAL 6MM MT2": 24000,
        "CRISTAL 8MM MT2": 45000,
        "CRISTAL 10MM MT2": 48000,
        "CRISTAL LAMINADO 6MM MT2": 35000,
        "CRISTAL LAMINADO 8MM MT2": 42000,
        "CRISTAL LAMINADO 10MM MT2": 68000,
        "CRISTAL TEMPLADO 5MM MT2": 80000,
        "CRISTAL TEMPLADO 8MM MT2": 95000,
        "CRISTAL TEMPLADO 10MM MT2": 115000,
    },
    "Espejos": {
        "ESPEJO 3MM MT2": 50000,
        "ESPEJO 4MM MT2": 60000,
        "ESPEJO 5MM MT2": 65000,
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
