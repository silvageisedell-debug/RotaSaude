from django.contrib import messages
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from contas.models import Modulo
from contas.permissoes import modulo_requerido
from portal.forms import MotivoForm

from .forms import MotoristaForm, PedidoPontoForm, PontoEmbarqueForm, VeiculoForm
from .models import Motorista, PedidoPontoEmbarque, PontoEmbarque, Veiculo

frota_requerida = modulo_requerido(Modulo.FROTA)


# ---------- Veículos ----------

@frota_requerida
def veiculos(request):
    form = VeiculoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Veículo cadastrado.")
        return redirect("frota:veiculos")
    lista = Veiculo.objects.select_related("modelo__marca")
    return render(request, "frota/veiculos.html", {
        "form": form,
        "veiculos": lista,
        "status_opcoes": Veiculo.Status.choices,
        "abrir_form": form.is_bound,
    })


@frota_requerida
def editar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    form = VeiculoForm(request.POST or None, instance=veiculo)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Veículo atualizado.")
        return redirect("frota:veiculos")
    return render(request, "frota/form.html", {
        "form": form,
        "titulo": "Editar veículo",
        "subtitulo": str(veiculo),
        "voltar": "frota:veiculos",
    })


@frota_requerida
def apagar_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    if request.method == "POST":
        try:
            veiculo.delete()
        except ProtectedError:
            messages.error(request, "Este veículo já tem viagens registradas e não pode ser apagado. Coloque-o em manutenção.")
        else:
            messages.success(request, "Veículo apagado.")
        return redirect("frota:veiculos")
    return render(request, "frota/confirmar_apagar.html", {"objeto": veiculo, "voltar": "frota:veiculos"})


@frota_requerida
@require_POST
def status_veiculo(request, pk):
    veiculo = get_object_or_404(Veiculo, pk=pk)
    novo = request.POST.get("status")
    if novo in Veiculo.Status.values:
        veiculo.status = novo
        veiculo.save(update_fields=["status"])
        messages.success(request, f"{veiculo.placa_formatada}: status {veiculo.get_status_display().lower()}.")
    return redirect("frota:veiculos")


# ---------- Motoristas ----------

@frota_requerida
def motoristas(request):
    form = MotoristaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Motorista cadastrado.")
        return redirect("frota:motoristas")
    return render(request, "frota/motoristas.html", {
        "form": form,
        "motoristas": Motorista.objects.filter(ativo=True),
        "abrir_form": form.is_bound,
    })


@frota_requerida
def editar_motorista(request, pk):
    motorista = get_object_or_404(Motorista, pk=pk)
    form = MotoristaForm(request.POST or None, instance=motorista)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Motorista atualizado.")
        return redirect("frota:motoristas")
    return render(request, "frota/form.html", {
        "form": form,
        "titulo": "Editar motorista",
        "subtitulo": f"ID {motorista.codigo}",
        "voltar": "frota:motoristas",
    })


# ---------- Pontos de embarque ----------

@frota_requerida
def pontos(request):
    form = PontoEmbarqueForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Ponto de embarque cadastrado.")
        return redirect("frota:pontos")
    pedidos = PedidoPontoEmbarque.objects.select_related("solicitante")
    return render(request, "frota/pontos.html", {
        "form": form,
        "pontos": PontoEmbarque.objects.filter(ativo=True),
        "pedidos_pendentes": pedidos.filter(status=PedidoPontoEmbarque.Status.PENDENTE),
        "pedidos_respondidos": pedidos.exclude(status=PedidoPontoEmbarque.Status.PENDENTE)[:3],
        "abrir_form": form.is_bound,
    })


@frota_requerida
def editar_ponto(request, pk):
    ponto = get_object_or_404(PontoEmbarque, pk=pk, ativo=True)
    form = PontoEmbarqueForm(request.POST or None, instance=ponto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Ponto de embarque atualizado. As solicitações em aberto já mostram o novo nome.")
        return redirect("frota:pontos")
    return render(request, "frota/form.html", {
        "form": form,
        "titulo": "Editar ponto de embarque",
        "subtitulo": ponto.nome,
        "voltar": "frota:pontos",
    })


@frota_requerida
def remover_ponto(request, pk):
    ponto = get_object_or_404(PontoEmbarque, pk=pk, ativo=True)
    if PontoEmbarque.objects.filter(ativo=True).count() <= 1:
        messages.error(request, "Mantenha pelo menos um ponto de embarque.")
        return redirect("frota:pontos")
    em_aberto = ponto.solicitacoes.filter(status__in=["pendente", "aprovada", "agendada"]).count()
    if request.method == "POST":
        # Desativa em vez de apagar: as solicitações antigas continuam apontando para o local.
        ponto.ativo = False
        ponto.save(update_fields=["ativo"])
        messages.success(request, "Ponto de embarque removido.")
        return redirect("frota:pontos")
    return render(request, "frota/confirmar_apagar.html", {
        "objeto": ponto,
        "voltar": "frota:pontos",
        "aviso": (
            f"Há {em_aberto} solicitação(ões) em aberto usando este local. Elas continuam com ele."
            if em_aberto else ""
        ),
        "acao": "Remover",
    })


@frota_requerida
@require_POST
def aprovar_pedido(request, pk):
    pedido = get_object_or_404(PedidoPontoEmbarque, pk=pk, status=PedidoPontoEmbarque.Status.PENDENTE)
    form = PontoEmbarqueForm({"nome": pedido.nome, "endereco": pedido.endereco, "cep": pedido.cep})
    if not form.is_valid():
        messages.error(request, " ".join(e for erros in form.errors.values() for e in erros))
        return redirect("frota:pontos")
    with transaction.atomic():
        form.save()
        pedido.status = PedidoPontoEmbarque.Status.APROVADO
        pedido.respondido_por = request.user
        pedido.save(update_fields=["status", "respondido_por"])
    messages.success(request, "Ponto cadastrado e disponível nas solicitações.")
    return redirect("frota:pontos")


@frota_requerida
def recusar_pedido(request, pk):
    pedido = get_object_or_404(PedidoPontoEmbarque, pk=pk, status=PedidoPontoEmbarque.Status.PENDENTE)
    form = MotivoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pedido.status = PedidoPontoEmbarque.Status.RECUSADO
        pedido.motivo_recusa = form.cleaned_data["motivo"]
        pedido.respondido_por = request.user
        pedido.save(update_fields=["status", "motivo_recusa", "respondido_por"])
        messages.success(request, "Pedido recusado.")
        return redirect("frota:pontos")
    return render(request, "parciais/recusar.html", {
        "form": form,
        "titulo": f"Recusar pedido: {pedido.nome}",
        "explicacao": "O motivo aparece para quem pediu.",
        "placeholder": "Ex.: já existe um ponto próximo",
        "voltar": "frota:pontos",
    })


@modulo_requerido(Modulo.SOLICITACOES)
def solicitar_ponto(request):
    """Atendente pede um local de coleta que ainda não está na lista."""
    form = PedidoPontoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pedido = form.save(commit=False)
        pedido.solicitante = request.user
        pedido.save()
        messages.success(request, "Pedido enviado ao administrador.")
        return redirect("frota:solicitar_ponto")
    meus = PedidoPontoEmbarque.objects.filter(solicitante=request.user)[:5]
    return render(request, "frota/solicitar_ponto.html", {"form": form, "meus_pedidos": meus})
