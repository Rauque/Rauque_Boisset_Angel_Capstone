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
