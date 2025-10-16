# apps/pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("barandas/", views.barandas, name="barandas"),

    # nuevas
    path("muebles/", views.muebles, name="muebles"),
    path("shower-door/", views.shower_door, name="shower_door"),
    path("mamparas/", views.mamparas, name="mamparas"),
    path("reposicion-cristales/", views.reposicion_cristales, name="reposicion_cristales"),
    path("ventanas/corredera/", views.corredera, name="corredera"),
    path("ventanas/abatible/", views.abatible, name="abatible"),
    path("ventanas/oscilobatiente/", views.oscilobatiente, name="oscilobatiente"),
    path("ventanas/proyectante/", views.proyectante, name="proyectante"),
    path("ventanas/fija/", views.fija, name="fija"),
    path("ventanas/bow-window/", views.bow_window, name="bow_window"),
    path("ventanas/medio-punto/", views.medio_punto, name="medio_punto"),
]
