import pytest
from django.urls import reverse
from apps.catalog.models import Product, Category
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_product_list_filtra_activos(client):
    cat = Category.objects.create(name="Ventanas")
    Product.objects.create(
        category=cat, name="Ventana activa", material="ALU", glass_type="TEM",
        thickness="4", color="WHT", price=1000, is_active=True
    )
    Product.objects.create(
        category=cat, name="Ventana inactiva", material="ALU", glass_type="TEM",
        thickness="4", color="WHT", price=1000, is_active=False
    )
    url = reverse("catalog:catalog_list")
    resp = client.get(url)
    assert "Ventana activa" in resp.content.decode()
    assert "Ventana inactiva" not in resp.content.decode()

@pytest.mark.django_db
def test_product_detail_404(client):
    url = reverse("catalog:product_detail", args=["no-existe"])
    resp = client.get(url)
    assert resp.status_code == 404

@pytest.mark.django_db
def test_manage_products_superuser(client):
    user = User.objects.create_superuser("admin", "admin@test.com", "pass1234")
    client.force_login(user)
    url = reverse("catalog:catalog_manage")
    resp = client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_manage_products_no_superuser(client):
    user = User.objects.create_user("normal", "normal@test.com", "pass1234")
    client.force_login(user)
    url = reverse("catalog:catalog_manage")
    resp = client.get(url)
    assert resp.status_code == 403

def test_pytest_funciona():
    assert 1 == 1