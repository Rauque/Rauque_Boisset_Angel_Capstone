from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required   # ← importa esto
from .forms import SignUpForm
from django.http import JsonResponse
from django.contrib.auth.models import User

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

@login_required                                           # ← y este decorador
def profile(request):
    return render(request, "accounts/profile.html")

def check_username(request):
    username = (request.GET.get("username") or "").strip()
    taken = User.objects.filter(username__iexact=username).exists() if username else False
    return JsonResponse({"taken": taken})