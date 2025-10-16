from django.db import models
from decimal import Decimal

class QuoteRequest(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    telefono = models.CharField(max_length=50, blank=True)
    categoria = models.CharField(max_length=120, blank=True)
    mensaje = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.email}"

'''class CustomQuoteRequest(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    telefono = models.CharField(max_length=50, blank=True)
    tipo = models.CharField(max_length=120)
    ancho_mm = models.PositiveIntegerField()
    alto_mm = models.PositiveIntegerField()
    ubicacion = models.CharField(max_length=160, blank=True)
    detalles = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.nombre} - {self.tipo}"'''


PRODUCT_TYPES = (
    ("mirror", "Espejo"),
    ("window", "Ventana"),
)

EDGE_TYPES = (("polished", "Borde pulido"), ("beveled", "Biselado"))
FRAME_TYPES = (("none", "Sin marco"), ("aluminum", "Marco aluminio"), ("wood", "Marco madera"))
GLASS_TYPES = (
    ("tempered", "Templado"),
    ("laminated", "Laminado"),
    ("monolithic", "Monolítico"),
    ("termopanel", "Termopanel (DVH)"),
)
THICKNESS = (("3", "3 mm"), ("4", "4 mm"), ("5", "5 mm"), ("6", "6 mm"))
PERF_COLOR = (("blanco", "Blanco"), ("titanio", "Titanio"), ("madera", "Folio madera"))

class CustomQuoteRequest(models.Model):
    # los que ya tenías:
    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    telefono = models.CharField(max_length=40, blank=True)
    tipo = models.CharField(max_length=16, choices=PRODUCT_TYPES)

    # medidas
    ancho_mm = models.PositiveIntegerField()
    alto_mm = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField(default=1)

    # espejo
    marco = models.CharField(max_length=16, choices=FRAME_TYPES, blank=True)
    borde = models.CharField(max_length=16, choices=EDGE_TYPES, blank=True)

    # ventana
    cristal = models.CharField(max_length=16, choices=GLASS_TYPES, blank=True)
    espesor_mm = models.CharField(max_length=2, choices=THICKNESS, blank=True)
    color_perfileria = models.CharField(max_length=16, choices=PERF_COLOR, blank=True)

    ubicacion = models.CharField(max_length=120, blank=True)
    detalles = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.nombre}"
    
    def recalcular_precio(self):
        """
        Cálculo ejemplo (ajusta según reglas reales):
        - área en m² = ancho_mm * alto_mm / 1_000_000
        - tarifa base por tipo de cristal (ejemplo)
        - multiplicador por marco
        - multiplicar por cantidad
        Guarda price y devuelve el nuevo precio (Decimal).
        """
        ancho = Decimal(self.ancho_mm or 0)
        alto = Decimal(self.alto_mm or 0)
        if ancho <= 0 or alto <= 0:
            nuevo_precio = Decimal("0.00")
        else:
            area_m2 = (ancho * alto) / Decimal("1000000")  # mm² -> m²

            base_rates = {
                "tempered": Decimal("50"),
                "laminated": Decimal("60"),
                "standard": Decimal("40"),
            }
            cristal_key = (self.cristal or "").lower()
            base = base_rates.get(cristal_key, Decimal("50"))

            marco_key = (self.marco or "").lower()
            if "alu" in marco_key or "aluminum" in marco_key:
                marco_mult = Decimal("1.2")
            elif "pvc" in marco_key:
                marco_mult = Decimal("1.0")
            else:
                marco_mult = Decimal("1.0")

            cantidad = Decimal(self.cantidad or 1)
            nuevo_precio = (base * marco_mult) * area_m2 * cantidad

        # redondeo a 2 decimales
        self.price = nuevo_precio.quantize(Decimal("0.01"))
        # no es obligatorio hacer save aquí; lo dejamos para reflejar en DB
        self.save()
        return self.price

    def confirm(self):
        """
        Crea un pedido (Order) asociado a la cotización si no existe.
        Retorna el pedido.
        """
        if hasattr(self, "order"):
            return self.order
        order = Order.objects.create(quote=self, total_price=self.price, status="En revisión")
        return order


class Order(models.Model):
    quote = models.OneToOneField(CustomQuoteRequest, on_delete=models.CASCADE, related_name="order")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=64, default="En revisión")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.status} - {self.total_price}"
# ...existing code...
