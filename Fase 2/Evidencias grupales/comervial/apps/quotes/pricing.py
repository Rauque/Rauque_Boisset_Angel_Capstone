# apps/quotes/pricing.py
def mm_to_m(v): return (v or 0) / 1000.0
def area_m2(ancho, alto): return mm_to_m(ancho) * mm_to_m(alto)
def perimetro_m(ancho, alto): return 2*(mm_to_m(ancho) + mm_to_m(alto))

def calcular_precio_espejo(ancho, alto, cantidad, marco, borde):
    BASE_M2 = 55000
    BISSEL_M = 6500
    PULIDO_M = 3000
    ALU_M = 12000
    MAD_M = 18000
    a = area_m2(ancho, alto)
    p = perimetro_m(ancho, alto)
    total = a*BASE_M2
    if marco == "aluminum":
        total += p*ALU_M
    elif marco == "wood":
        total += p*MAD_M
    else:
        total += p*(BISSEL_M if borde == "beveled" else PULIDO_M)
    return round(total * (cantidad or 1))

def calcular_precio_ventana(ancho, alto, cantidad, cristal, espesor, color_perf):
    BASE = {"monolithic":38000, "tempered":78000, "laminated":95000, "termopanel":120000}
    MULT = {"3":1.0, "4":1.07, "5":1.15, "6":1.25}
    PERF = {"blanco":14000, "titanio":18000, "madera":22000}
    a = area_m2(ancho, alto)
    p = perimetro_m(ancho, alto)
    total = (BASE.get(cristal,0) * a) * MULT.get(str(espesor),1.0)
    total += p * PERF.get(color_perf,0)
    return round(total * (cantidad or 1))
