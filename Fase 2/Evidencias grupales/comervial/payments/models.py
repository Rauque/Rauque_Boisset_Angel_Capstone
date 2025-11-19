# payments/models.py
from django.db import models
from django.conf import settings
from apps.catalog.models import Product


class FlowOrder(models.Model):
    STATUS_CHOICES = [
        ("created", "Creado"),
        ("pending", "Pendiente"),
        ("paid", "Pagado"),
        ("failed", "Fallido"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="flow_orders",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="flow_orders",
    )

    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Lo que tú generas
    commerce_order = models.CharField(max_length=100, unique=True)

    # Lo que Flow devuelve (ej: 4594876)
    flow_order = models.CharField(max_length=50, blank=True, null=True)

    # token de Flow (por si lo quieres rastrear)
    token = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="created",
    )

    # Para guardar el JSON de Flow (getStatus)
    raw_response = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.id} - {self.product.name} - {self.get_status_display()}"
