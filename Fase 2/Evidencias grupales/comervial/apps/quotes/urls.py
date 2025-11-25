from django.urls import path
from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.cotizador, name="cotizador"),
    path("personalizado/", views.cotizador_personalizado, name="cotizador_personalizado"),
    path("pricing-rules/", views.pricing_rules, name="pricing_rules"),
]

