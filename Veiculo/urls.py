from django.urls import path
from . import views

urlpatterns = [
    path('Veiculo/', views.lista_veiculos, name='lista_veiculos'),
]

