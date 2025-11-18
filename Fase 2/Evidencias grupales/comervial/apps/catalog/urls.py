# apps/catalog/urls.py
from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # Gestión (debe ir antes del slug)
    path("gestionar/", views.manage_products, name="catalog_manage"),
    path("gestionar/crear/", views.product_create, name="product_create"),
    path("gestionar/<int:pk>/editar/", views.product_edit, name="product_edit"),
    path("gestionar/<int:pk>/eliminar/", views.product_delete, name="product_delete"),

    # Público
    path("", views.product_list, name="catalog_list"),
    path("<slug:slug>/", views.product_detail, name="product_detail"),
    path("pago/<int:pk>/pref/", views.mp_pref, name="mp_pref"),
    path("pago/exito/", views.mp_success, name="mp_success"),
    path("pago/error/", views.mp_failure, name="mp_failure"),
    path("pago/pendiente/", views.mp_pending, name="mp_pending"),
    path("pago/webhook/", views.mp_webhook, name="mp_webhook"),

    # Gestión (solo superusuario)
    path("gestionar/", views.manage_products, name="catalog_manage"),
    path("gestionar/crear/", views.product_create, name="product_create"),
    path("gestionar/<int:pk>/editar/", views.product_edit, name="product_edit"),
    path("gestionar/<int:pk>/eliminar/", views.product_delete, name="product_delete"),
]
