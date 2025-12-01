from django.conf import settings
from django.db import models


REGION_CHOICES = [
    ("XV", "Arica y Parinacota"),
    ("I", "Tarapacá"),
    ("II", "Antofagasta"),
    ("III", "Atacama"),
    ("IV", "Coquimbo"),
    ("V", "Valparaíso"),
    ("RM", "Región Metropolitana"),
    ("VI", "O'Higgins"),
    ("VII", "Maule"),
    ("XVI", "Ñuble"),
    ("VIII", "Biobío"),
    ("IX", "La Araucanía"),
    ("XIV", "Los Ríos"),
    ("X", "Los Lagos"),
    ("XI", "Aysén"),
    ("XII", "Magallanes"),
]


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )

    full_name = models.CharField("Nombre completo", max_length=150, blank=True)
    rut = models.CharField("RUT", max_length=12, blank=True)
    phone = models.CharField("Teléfono", max_length=20, blank=True)

    address = models.CharField("Dirección", max_length=255, blank=True)
    comuna = models.CharField("Comuna", max_length=100, blank=True)
    region = models.CharField(
        "Región",
        max_length=10,
        choices=REGION_CHOICES,
        blank=True,
    )

    country = models.CharField(
        "País",
        max_length=50,
        default="Chile",
        editable=False,  # bloqueado en Chile
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de cliente"
        verbose_name_plural = "Perfiles de cliente"

    def __str__(self):
        return f"Perfil de {self.user.username}"
