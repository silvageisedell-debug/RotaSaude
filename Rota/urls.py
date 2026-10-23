from django.urls import path

from . import views

urlpatterns = [
    path("disponibilidade/nova/", views.nova_disponibilidade, name="nova_disponibilidade"),
    path("rotas/", views.lista_rotas, name="lista_rotas"),
    path("rotas/nova/", views.nova_rota, name="nova_rota"),
]
