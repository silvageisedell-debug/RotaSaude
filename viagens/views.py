from datetime import timedelta

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
from django.views.decorators.http import require_POST

from contas.models import Modulo
from contas.permissoes import modulo_requerido
from solicitacoes.models import Solicitacao

from . import services
from .forms import ProgramarViagemForm
from .models import HORA_FIM, HORA_INICIO, Viagem

viagens_requerido = modulo_requerido(Modulo.VIAGENS)


def _data_param(request, nome="data"):
    return parse_date(request.GET.get(nome) or "") or timezone.localdate()


@viagens_requerido
def quadro(request):
    """Quadro de horários do dia: uma linha por veículo e uma barra por viagem."""
    dia = _data_param(request)
    viagens = Viagem.objects.filter(data=dia).exclude(status=Viagem.Status.CANCELADA).select_related("motorista")
    situacao = services.disponibilidade(dia)
    linhas = [
        {"situacao": s, "viagens": [v for v in viagens if v.veiculo_id == s.objeto.pk]}
        for s in situacao["veiculos"]
    ]
    return render(request, "viagens/quadro.html", {
        "dia": dia,
        "anterior": dia - timedelta(days=1),
        "seguinte": dia + timedelta(days=1),
        "hoje": timezone.localdate(),
        "linhas": linhas,
        "horas": range(HORA_INICIO, HORA_FIM),
        "disponibilidade": situacao,
        "titulo_disponibilidade": f"Disponibilidade em {dia:%d/%m/%Y}",
    })


@viagens_requerido
def programar(request):
    pre = None
    if request.GET.get("solicitacao", "").isdigit():
        pre = Solicitacao.objects.filter(
            pk=int(request.GET["solicitacao"]),
            status__in=[Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA],
        ).first()
    form = ProgramarViagemForm(request.POST or None, preselecionada=pre)
    if request.method == "POST" and form.is_valid():
        dados = form.cleaned_data
        try:
            viagem = services.programar_viagem(
                data=dados["data"],
                saida=dados["saida"],
                duracao_horas=dados["duracao_horas"],
                veiculo=dados["veiculo"],
                motorista=dados["motorista"],
                solicitacoes=list(dados["solicitacoes"]),
                usuario=request.user,
            )
        except ValueError as erro:
            for mensagem in erro.args[0]:
                form.add_error(None, mensagem)
        else:
            messages.success(request, f"{viagem.codigo} programada.")
            return redirect(f"{reverse('viagens:quadro')}?data={viagem.data:%Y-%m-%d}")
    selecionadas = [str(pk) for pk in (form["solicitacoes"].value() or [])]
    return render(request, "viagens/programar.html", {"form": form, "selecionadas": selecionadas})


@viagens_requerido
def disponibilidade_json(request):
    """Lista de veículos e motoristas livres ou ocupados na janela pedida (usada pelo seletor)."""
    dia = _data_param(request)
    saida = parse_time(request.GET.get("saida") or "")
    try:
        duracao = max(1, min(12, int(request.GET.get("duracao", "1"))))
    except ValueError:
        duracao = 1
    situacao = services.disponibilidade(dia, saida, duracao)

    def linha(s, nome, info):
        return {"id": s.objeto.pk, "nome": nome, "info": info, "status": s.status, "livre": s.livre}

    return JsonResponse({
        "veiculos": [
            linha(s, str(s.objeto.modelo), f"{s.objeto.placa_formatada} · {s.objeto.capacidade} lugares"
                  + (f" · {s.detalhe}" if s.detalhe else ""))
            for s in situacao["veiculos"]
        ],
        "motoristas": [linha(s, s.objeto.nome, s.detalhe) for s in situacao["motoristas"]],
    })


@viagens_requerido
def detalhe(request, pk):
    viagem = get_object_or_404(Viagem.objects.select_related("veiculo__modelo__marca", "motorista"), pk=pk)
    return render(request, "viagens/detalhe.html", {
        "viagem": viagem,
        "passageiros": viagem.passageiros.select_related("ponto_embarque", "destino"),
        "paradas": viagem.paradas.all(),
    })


def _acao(request, pk, funcao, sucesso):
    viagem = get_object_or_404(Viagem, pk=pk)
    try:
        funcao(viagem, request.user)
    except ValueError as erro:
        for mensagem in erro.args[0]:
            messages.error(request, mensagem)
    else:
        messages.success(request, sucesso)
    return redirect("viagens:detalhe", pk=pk)


@viagens_requerido
@require_POST
def iniciar(request, pk):
    return _acao(request, pk, services.iniciar_viagem, "Viagem iniciada. Marque quem embarcou.")


@viagens_requerido
@require_POST
def concluir(request, pk):
    return _acao(request, pk, services.concluir_viagem, "Viagem concluída. Quem não embarcou voltou para aprovadas.")


@viagens_requerido
@require_POST
def cancelar(request, pk):
    viagem = get_object_or_404(Viagem, pk=pk)
    try:
        services.cancelar_viagem(viagem, request.user)
    except ValueError as erro:
        messages.error(request, erro.args[0][0])
        return redirect("viagens:detalhe", pk=pk)
    messages.success(request, "Viagem cancelada. Os pacientes voltaram para aprovadas.")
    return redirect(f"{reverse('viagens:quadro')}?data={viagem.data:%Y-%m-%d}")


@viagens_requerido
@require_POST
def embarque(request, pk, solicitacao_pk):
    viagem = get_object_or_404(Viagem, pk=pk)
    solicitacao = get_object_or_404(Solicitacao, pk=solicitacao_pk, viagem=viagem)
    try:
        embarcou = services.alternar_embarque(viagem, solicitacao)
    except ValueError as erro:
        messages.error(request, erro.args[0][0])
    else:
        messages.success(request, f"{solicitacao.paciente}: {'embarcou' if embarcou else 'embarque desfeito'}.")
    return redirect("viagens:detalhe", pk=pk)
