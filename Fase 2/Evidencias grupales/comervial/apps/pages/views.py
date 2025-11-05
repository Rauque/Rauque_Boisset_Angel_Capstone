from django.shortcuts import render

def index(request):
    return render(request, "pages/index.html")

def barandas(request):
    return render(request, "pages/barandas.html")

def muebles(request):
    return render(request, "pages/muebles.html")

def shower_door(request):
    return render(request, "pages/shower_door.html")

def mamparas(request):
    return render(request, "pages/mamparas.html")

def reposicion_cristales(request):
    return render(request, "pages/reposicion_cristales.html")

def corredera(request):       return render(request, "pages/ventanas/corredera.html")
def abatible(request):        return render(request, "pages/ventanas/abatible.html")
def oscilobatiente(request):  return render(request, "pages/ventanas/oscilobatiente.html")
def proyectante(request):     return render(request, "pages/ventanas/proyectante.html")
def fija(request):            return render(request, "pages/ventanas/fija.html")
def bow_window(request):      return render(request, "pages/ventanas/bow_window.html")
def medio_punto(request):     return render(request, "pages/ventanas/medio_punto.html")

def puertas_abatibles(request):
    return render(request, "pages/puertas/abatibles.html")

def puertas_correderas(request):
    return render(request, "pages/puertas/correderas.html")

def puertas_elevadoras(request):
    return render(request, "pages/puertas/elevadoras.html")

def puertas_templado(request):
    return render(request, "pages/puertas/templado.html")