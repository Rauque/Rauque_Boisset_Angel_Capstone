from django.contrib import admin
from .models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "rut", "phone", "comuna", "region", "updated_at")
    search_fields = ("user__username", "full_name", "rut", "phone", "comuna")
    list_filter = ("region",)
