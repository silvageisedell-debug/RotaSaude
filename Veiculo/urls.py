from django.urls import path
from . import views

urlpatterns = [
    path("Veiculo/", views.lista_veiculos, name="lista_veiculos"),
    path("Veiculo/nova/", views.novo_veiculo, name="novo_veiculo"),
]
