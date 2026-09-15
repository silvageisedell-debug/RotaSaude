from django.urls import path
from . import views

urlpatterns = [
    path("Veiculo/", views.lista_veiculos, name="lista_veiculos"),
    path("Veiculo/nova/", views.novo_veiculo, name="novo_veiculo"),
    path("Veiculo/<int:pk>/editar/", views.editar_veiculo, name="editar_veiculo"),
    path("Veiculo/<int:pk>/apagar/", views.apagar_veiculo, name="apagar_veiculo"),

]
