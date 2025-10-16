from django.contrib import admin
from .models import CustomQuoteRequest, Order

@admin.register(CustomQuoteRequest)
class CustomQuoteRequestAdmin(admin.ModelAdmin):
    # Evitar 'price' si el modelo no lo tiene; usar campos seguros que existen
    list_display = ("nombre", "email", "tipo", "aprobado", "created_at")
    list_filter = ("aprobado", "tipo", "created_at")
    search_fields = ("nombre", "email", "tipo")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("quote", "total_price", "status", "created_at")
    list_filter = ("status", "created_at")