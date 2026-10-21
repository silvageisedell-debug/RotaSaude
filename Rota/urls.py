from django.urls import path

from . import views

urlpatterns = [
    path("disponibilidade/nova/", views.nova_disponibilidade, name="nova_disponibilidade"),
]
