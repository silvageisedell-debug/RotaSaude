from django.shortcuts import render
from .models import Veiculo, Marca, Modelo

def lista_veiculos(request):
    # Use letras minúsculas e no plural para a variável da lista
    veiculos = Veiculo.objects.all() 
    return render(request, "Veiculo/lista.html", {"veiculos": veiculos})

