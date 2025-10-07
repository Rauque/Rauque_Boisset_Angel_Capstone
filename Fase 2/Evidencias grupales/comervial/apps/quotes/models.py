from django.db import models

class QuoteRequest(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    telefono = models.CharField(max_length=50, blank=True)
    categoria = models.CharField(max_length=120, blank=True)
    mensaje = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.email}"

class CustomQuoteRequest(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    telefono = models.CharField(max_length=50, blank=True)
    tipo = models.CharField(max_length=120)
    ancho_mm = models.PositiveIntegerField()
    alto_mm = models.PositiveIntegerField()
    ubicacion = models.CharField(max_length=160, blank=True)
    detalles = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.tipo}"


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

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.nombre}"
