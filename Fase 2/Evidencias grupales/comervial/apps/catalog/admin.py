from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name","category","material","glass_type","thickness","color","price","is_active")
    list_filter = ("category","material","glass_type","thickness","color","is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
