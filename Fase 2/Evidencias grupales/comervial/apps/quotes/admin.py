from django.contrib import admin
from .models import CustomQuoteRequest, Order

@admin.register(CustomQuoteRequest)
class CustomQuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "tipo", "price", "aprobado", "created_at")
    list_filter = ("aprobado", "tipo", "created_at")
    search_fields = ("nombre", "email")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("quote", "total_price", "status", "created_at")
    list_filter = ("status", "created_at")