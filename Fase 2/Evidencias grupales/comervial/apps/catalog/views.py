# apps/catalog/views.py
from django.contrib import messages
from .forms import ProductForm
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import (
    Product, Category,
    MATERIAL_CHOICES, GLASS_CHOICES, THICKNESS_CHOICES, COLOR_CHOICES
)

def product_list(request):
    qs = Product.objects.filter(is_active=True)

    # Filtros por querystring
    material  = request.GET.get("material")  or ""
    glass     = request.GET.get("cristal")   or ""
    thickness = request.GET.get("espesor")   or ""
    color     = request.GET.get("color")     or ""
    category  = request.GET.get("categoria") or ""

    if material:  qs = qs.filter(material=material)
    if glass:     qs = qs.filter(glass_type=glass)
    if thickness: qs = qs.filter(thickness=thickness)
    if color:     qs = qs.filter(color=color)
    if category:  qs = qs.filter(category__slug=category)

    paginator = Paginator(qs.select_related("category"), 12)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    ctx = {
        "products": products,
        "categories": Category.objects.all(),
        "MATERIAL_CHOICES": MATERIAL_CHOICES,
        "GLASS_CHOICES": GLASS_CHOICES,
        "THICKNESS_CHOICES": THICKNESS_CHOICES,
        "COLOR_CHOICES": COLOR_CHOICES,
        "current": {
            "material": material, "cristal": glass, "espesor": thickness,
            "color": color, "categoria": category
        },
    }
    return render(request, "catalog/list.html", ctx)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "catalog/detail.html", {"product": product})
# Funciones de administración (solo para superusuarios)


def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_superuser)
def manage_products(request):
    qs = Product.objects.all().select_related("category").order_by("-created_at")
    return render(request, "catalog/manage_list.html", {"products": qs})

@login_required
@user_passes_test(is_superuser)
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto creado correctamente.")
        return redirect("catalog:catalog_manage")
    return render(request, "catalog/product_form.html", {"form": form, "title": "Nuevo producto"})

@login_required
@user_passes_test(is_superuser)
def product_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado.")
        return redirect("catalog:catalog_manage")
    return render(request, "catalog/product_form.html", {"form": form, "title": "Editar producto"})

@login_required
@user_passes_test(is_superuser)
def product_delete(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Producto eliminado.")
        return redirect("catalog:catalog_manage")
    return render(request, "catalog/product_delete_confirm.html", {"product": obj})
