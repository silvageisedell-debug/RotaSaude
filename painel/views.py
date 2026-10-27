from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from contas.models import Modulo
from contas.urls_inicio import url_inicial
from frota.models import Veiculo
from solicitacoes.models import HistoricoSolicitacao, Solicitacao
from viagens.models import Viagem
from viagens.services import disponibilidade

CORES_STATUS = {
    "pendente": "#F59E0B",
    "aprovada": "#0EA5E9",
    "agendada": "#8B5CF6",
    "em_viagem": "#14B8A6",
    "concluida": "#16A34A",
    "negada": "#E11D48",
}


def raiz(request):
    if not request.user.is_authenticated:
        return redirect("contas:login")
    return redirect(url_inicial(request.user))


@login_required
def inicio(request):
    if not request.user.pode(Modulo.INICIO):
        return redirect(url_inicial(request.user))
    hoje = timezone.localdate()
    contagem = {s: Solicitacao.objects.filter(status=s).count() for s in Solicitacao.FLUXO}
    viagens_hoje = (
        Viagem.objects.filter(data=hoje).exclude(status=Viagem.Status.CANCELADA)
        .select_related("veiculo__modelo__marca", "motorista")
    )
    acao = Solicitacao.objects.filter(
        status__in=[Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA]
    ).select_related("destino", "categoria")
    grafico = {
        "rotulos": [s.label for s in Solicitacao.FLUXO],
        "valores": [contagem[s] for s in Solicitacao.FLUXO],
        "cores": [CORES_STATUS[s] for s in Solicitacao.FLUXO],
    }
    return render(request, "painel/inicio.html", {
        "kpi_pendentes": contagem[Solicitacao.Status.PENDENTE],
        "kpi_viagens_hoje": viagens_hoje.count(),
        "kpi_veiculos": Veiculo.objects.filter(status=Veiculo.Status.DISPONIVEL).count(),
        "kpi_concluidas": contagem[Solicitacao.Status.CONCLUIDA],
        "disponibilidade": disponibilidade(hoje),
        "viagens_hoje": viagens_hoje,
        "precisam_acao": acao,
        "grafico": grafico,
        "hoje": hoje,
    })


@login_required
def resumo(request):
    """'Recuperar': o que está aguardando ação, as viagens de hoje e as últimas ações do usuário."""
    hoje = timezone.localdate()
    pendentes = Solicitacao.objects.filter(
        status__in=[Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA]
    ).select_related("destino")
    viagens = Viagem.objects.filter(data=hoje, status__in=Viagem.ATIVAS).select_related("veiculo__modelo__marca", "motorista")
    acoes = HistoricoSolicitacao.objects.filter(usuario=request.user).select_related("solicitacao").order_by("-criado_em")[:6]
    linhas = [f"RotaSaúde - resumo de {timezone.localtime():%d/%m/%Y %H:%M}", "", f"Pedidos aguardando ação ({len(pendentes)}):"]
    linhas += [f"- {s.codigo} · {s.paciente} · {s.destino} · {s.data:%d/%m/%Y} {s.horario:%H:%M} · {s.get_status_display()}" for s in pendentes] or ["- Nenhum"]
    linhas += ["", f"Viagens de hoje ({len(viagens)}):"]
    linhas += [f"- {v.codigo} · {v.destino} · {v.saida:%H:%M} · {v.veiculo} · {v.motorista} · {v.get_status_display()}" for v in viagens] or ["- Nenhuma"]
    return render(request, "painel/resumo.html", {
        "pendentes": pendentes,
        "viagens": viagens,
        "acoes": acoes,
        "texto_resumo": "\n".join(linhas),
    })


@login_required
def sem_modulo(request):
    return render(request, "painel/sem_modulo.html")
