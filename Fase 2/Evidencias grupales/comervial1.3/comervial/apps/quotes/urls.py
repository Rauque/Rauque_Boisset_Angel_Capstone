from django.urls import path
from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.cotizador, name="cotizador"),
    path("personalizado/", views.cotizador_personalizado, name="cotizador_personalizado"),
    path("ok/", views.cotizador_ok, name="cotizador_ok"), 
    path("pricing-rules/", views.pricing_rules, name="pricing_rules"),

    path(
        "personalizado/historial/<int:pk>/",
        views.personalized_quote_detail,
        name="personalized_quote_detail",
    ),
    path(
        "personalizado/historial/<int:pk>/pdf/",
        views.personalized_quote_pdf,
        name="personalized_quote_pdf",
    ),
]

