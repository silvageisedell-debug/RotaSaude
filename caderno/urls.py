from django.urls import path

from . import views

app_name = "caderno"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("avisado/", views.avisado, name="avisado"),
    path("<int:pk>/concluir/", views.concluir, name="concluir"),
    path("<int:pk>/apagar/", views.apagar, name="apagar"),
    path("<int:pk>/adiar/", views.adiar, name="adiar"),
]
