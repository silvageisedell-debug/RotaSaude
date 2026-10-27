from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("painel.urls")),
    path("contas/", include("contas.urls")),
    path("frota/", include("frota.urls")),
    path("solicitacoes/", include("solicitacoes.urls")),
    path("viagens/", include("viagens.urls")),
    path("caderno/", include("caderno.urls")),
]
