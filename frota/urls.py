from django.urls import path

from . import views

app_name = "frota"

urlpatterns = [
    path("veiculos/", views.veiculos, name="veiculos"),
    path("veiculos/<int:pk>/editar/", views.editar_veiculo, name="editar_veiculo"),
    path("veiculos/<int:pk>/apagar/", views.apagar_veiculo, name="apagar_veiculo"),
    path("veiculos/<int:pk>/status/", views.status_veiculo, name="status_veiculo"),
    path("motoristas/", views.motoristas, name="motoristas"),
    path("motoristas/<int:pk>/editar/", views.editar_motorista, name="editar_motorista"),
    path("pontos/", views.pontos, name="pontos"),
    path("pontos/<int:pk>/editar/", views.editar_ponto, name="editar_ponto"),
    path("pontos/<int:pk>/remover/", views.remover_ponto, name="remover_ponto"),
    path("pontos/solicitar/", views.solicitar_ponto, name="solicitar_ponto"),
    path("pontos/pedidos/<int:pk>/aprovar/", views.aprovar_pedido, name="aprovar_pedido"),
    path("pontos/pedidos/<int:pk>/recusar/", views.recusar_pedido, name="recusar_pedido"),
]
