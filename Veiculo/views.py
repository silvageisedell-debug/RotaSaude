from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from Rota.acesso import exige, papel
from Rota.models import Disponibilidade, Viagem

from .models import Veiculo
from .forms import VeiculoForm


@exige("admin", "atendente")
def painel(request):
    hoje = timezone.localdate()
    return render(request, "Veiculo/painel.html", {
        "total_veiculos": Veiculo.objects.count(),
        "total_rotas": Viagem.objects.count(),
        "vagas_hoje": Disponibilidade.objects.filter(data=hoje).aggregate(total=Sum("vagas"))["total"] or 0,
        "rotas_recentes": Viagem.objects.select_related("categoria", "disponibilidade__veiculo")[:5],
        "veiculos": Veiculo.objects.select_related("modelo__marca"),
    })


def entrar(request):
    if request.user.is_authenticated and papel(request.user):
        return redirect("painel")
    erro = None
    if request.method == "POST":
        usuario = authenticate(
            request,
            username=(request.POST.get("username") or "").strip(),
            password=request.POST.get("password") or "",
        )
        if usuario is None or not papel(usuario):
            erro = "E-mail ou senha incorretos."
        else:
            login(request, usuario)
            return redirect("painel")
    return render(request, "Veiculo/entrar.html", {"erro": erro})


class Sair(LogoutView):
    next_page = "entrar"


@exige("admin", "atendente")
def lista_veiculos(request):
    veiculos = Veiculo.objects.all()
    return render(request, "Veiculo/lista.html", {"veiculos": veiculos})


@exige("admin")
def novo_veiculo(request):
    form = VeiculoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Veículo cadastrado.")
        return redirect("lista_veiculos")
    return render(request, "Veiculo/nova.html", {"form": form})


@exige("admin")
def editar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    form = VeiculoForm(request.POST or None, instance=veiculo)
    if form.is_valid():
        form.save()
        messages.success(request, "Veículo atualizado.")
        return redirect("lista_veiculos")
    return render(request, "Veiculo/nova.html", {"form": form})


@exige("admin")
def apagar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == "POST":
        veiculo.delete()
        messages.success(request, "Veículo apagado.")
        return redirect("lista_veiculos")
    return render(request, "Veiculo/confirmar_apagar.html", {"veiculo": veiculo})
