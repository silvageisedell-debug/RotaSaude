from django.shortcuts import render, redirect, get_object_or_404
from .models import Veiculo
from .forms import VeiculoForm


def lista_veiculos(request):
    veiculos = Veiculo.objects.all()
    form = VeiculoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("lista_veiculos")
    return render(
        request,
        "Veiculo/lista.html",
        {"veiculos": veiculos, "form": form},
    )


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


def disponibilidade_veiculo(request):
    veiculos = Veiculo.objects.all()
    sucesso = False
    erro = None

    if request.method == "POST":
        veiculo_id = request.POST.get("veiculo")
        data = request.POST.get("data")
        horario = request.POST.get("horario")

        if not veiculo_id or not data or not horario:
            erro = "Por favor, preencha todos os campos obrigatórios."
        else:
            sucesso = True

    return render(
        request,
        "Veiculo/disponibilidade.html",
        {"veiculos": veiculos, "sucesso": sucesso, "erro": erro},
    )

