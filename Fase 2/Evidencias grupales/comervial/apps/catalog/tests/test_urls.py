from django.urls import reverse, resolve
from apps.catalog import views

def test_catalog_list_url_resuelve():
    url = reverse("catalog:catalog_list")
    assert resolve(url).func == views.product_list

def test_catalog_detail_url_resuelve():
    url = reverse("catalog:product_detail", args=["ventana-aluminio"])
    assert resolve(url).func == views.product_detail

def test_catalog_manage_url_resuelve():
    url = reverse("catalog:catalog_manage")
    assert resolve(url).func == views.manage_products

def test_pytest_funciona():
    assert 1 == 1