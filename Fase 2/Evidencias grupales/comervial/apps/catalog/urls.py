# apps/catalog/urls.py
from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # Público
    path("", views.product_list, name="catalog_list"),

    # Gestión (van antes del slug)
    path("gestionar/", views.manage_products, name="catalog_manage"),
    path("gestionar/crear/", views.product_create, name="product_create"),
    path("gestionar/<int:pk>/editar/", views.product_edit, name="product_edit"),
    path("gestionar/<int:pk>/eliminar/", views.product_delete, name="product_delete"),

    # Detalle (catch-all) al final
    path("<slug:slug>/", views.product_detail, name="product_detail"),
]
