from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User

from payments.models import FlowOrder          # <-- así, SIN "apps."
from apps.quotes.models import PersonalizedQuote

from .forms import SignUpForm, CustomerProfileForm
from .models import CustomerProfile


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cuenta creada con éxito. ¡Bienvenido!")
            return redirect("index")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})

@login_required
def profile(request):
    orders = (
        FlowOrder.objects
        .filter(user=request.user)
        .select_related("product")
        .order_by("-created_at")
    )

    personalized_quotes = PersonalizedQuote.objects.filter(user=request.user)

    context = {
        "orders": orders,
        "personalized_quotes": personalized_quotes,
    }
    return render(request, "accounts/profile.html", context)


def check_username(request):
    username = (request.GET.get("username") or "").strip()
    taken = User.objects.filter(username__iexact=username).exists() if username else False
    return JsonResponse({"taken": taken})

@login_required
def profile(request):
    # compras Flow
    orders = (
        FlowOrder.objects
        .filter(user=request.user)
        .select_related("product")
        .order_by("-created_at")
    )

    # cotizaciones personalizadas
    personalized_quotes = PersonalizedQuote.objects.filter(user=request.user)

    # perfil de cliente (si no existe, se crea vacío)
    customer_profile, created = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=customer_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos de cliente se actualizaron correctamente.")
            return redirect("profile")  # SIN namespace, porque accounts/urls no tiene app_name
    else:
        form = CustomerProfileForm(instance=customer_profile)

    context = {
        "orders": orders,
        "personalized_quotes": personalized_quotes,
        "customer_profile": customer_profile,
        "profile_form": form,
    }
    return render(request, "accounts/profile.html", context)
