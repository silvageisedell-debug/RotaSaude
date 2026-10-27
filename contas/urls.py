from django.urls import path

from . import views

app_name = "contas"

urlpatterns = [
    path("entrar/", views.entrar, name="login"),
    path("sair/", views.sair, name="sair"),
    path("solicitar-acesso/", views.solicitar_acesso, name="solicitar_acesso"),
    path("usuarios/", views.usuarios, name="usuarios"),
    path("usuarios/<int:pk>/acesso/", views.alternar_acesso, name="alternar_acesso"),
    path("permissoes/", views.permissoes, name="permissoes"),
]
