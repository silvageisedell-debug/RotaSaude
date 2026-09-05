from django.shortcuts import render, redirect
from .models import Veiculo
from .forms import VeiculoForm


def lista_veiculos(request):
    veiculos = Veiculo.objects.all()
    return render(request, "Veiculo/lista.html", {"veiculos": veiculos})


def novo_veiculo(request):
    form = VeiculoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("lista_veiculos")
    return render(request, "Veiculo/nova.html", {"form": form})
