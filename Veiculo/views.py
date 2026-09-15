from django.shortcuts import render, redirect, get_object_or_404
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


def editar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    form = VeiculoForm(request.POST or None, instance=veiculo)
    if form.is_valid():
        form.save()
        return redirect("lista_veiculos")
    return render(request, "Veiculo/nova.html", {"form": form})


def apagar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == "POST":
        veiculo.delete()
        return redirect("lista_veiculos")
    return render(request, "Veiculo/confirmar_apagar.html", {"veiculo": veiculo})
