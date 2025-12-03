# payments/urls.py
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("flow/pagar/<int:pk>/", views.flow_pay_product, name="flow_pay_product"),
    path("flow/return/", views.flow_return, name="flow_return"),
    path("flow/confirm/", views.flow_confirm, name="flow_confirm"),
]
