from django.shortcuts import render

def index(request):
    return render(request, "pages/index.html")

def barandas(request):
    return render(request, "pages/barandas.html")
