from django.urls import path

from . import views

app_name = "painel"

urlpatterns = [
    path("", views.raiz, name="raiz"),
    path("inicio/", views.inicio, name="inicio"),
    path("resumo/", views.resumo, name="resumo"),
    path("sem-modulo/", views.sem_modulo, name="sem_modulo"),
]
