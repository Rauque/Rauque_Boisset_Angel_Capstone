from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required   # ← importa esto
from .forms import SignUpForm
from django.http import JsonResponse
from django.contrib.auth.models import User
from payments.models import FlowOrder


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
    return render(request, "accounts/profile.html", {"orders": orders})

def check_username(request):
    username = (request.GET.get("username") or "").strip()
    taken = User.objects.filter(username__iexact=username).exists() if username else False
    return JsonResponse({"taken": taken})