from django.urls import path

from . import views

app_name = "viagens"

urlpatterns = [
    path("", views.quadro, name="quadro"),
    path("programar/", views.programar, name="programar"),
    path("disponibilidade/", views.disponibilidade_json, name="disponibilidade"),
    path("<int:pk>/", views.detalhe, name="detalhe"),
    path("<int:pk>/iniciar/", views.iniciar, name="iniciar"),
    path("<int:pk>/concluir/", views.concluir, name="concluir"),
    path("<int:pk>/cancelar/", views.cancelar, name="cancelar"),
    path("<int:pk>/embarque/<int:solicitacao_pk>/", views.embarque, name="embarque"),
]
