from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from contas.models import Modulo
from contas.permissoes import modulo_requerido
from portal.forms import MotivoForm
from portal.navegacao import voltar

from . import services
from .forms import SolicitacaoForm
from .models import Solicitacao

solicitacoes_requerido = modulo_requerido(Modulo.SOLICITACOES)


def _base():
    return Solicitacao.objects.select_related("destino", "ponto_embarque", "categoria", "viagem")


@solicitacoes_requerido
def lista(request):
    modo = request.GET.get("modo", "kanban")
    status = request.GET.get("status", "")
    busca = request.GET.get("q", "").strip()
    qs = _base()
    contexto = {"modo": modo, "status": status, "busca": busca}
    if modo == "lista":
        if status in Solicitacao.Status.values:
            qs = qs.filter(status=status)
        if busca:
            filtro = Q(paciente__icontains=busca) | Q(destino__nome__icontains=busca) | Q(destino__cidade__icontains=busca)
            codigo = busca.upper().removeprefix("SOL-")
            if codigo.isdigit():
                filtro |= Q(pk=int(codigo))
            qs = qs.filter(filtro)
        contexto["solicitacoes"] = qs
        contexto["filtros"] = [("", "Todas")] + [(s.value, s.label) for s in Solicitacao.FLUXO] + [
            (Solicitacao.Status.CANCELADA.value, Solicitacao.Status.CANCELADA.label)
        ]
    else:
        por_status = {s: [] for s in Solicitacao.FLUXO}
        for s in qs.filter(status__in=Solicitacao.FLUXO):
            por_status[s.status].append(s)
        contexto["colunas"] = [(s.label, por_status[s]) for s in Solicitacao.FLUXO]
    return render(request, "solicitacoes/lista.html", contexto)


@solicitacoes_requerido
def nova(request):
    form = SolicitacaoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        solicitacao = services.registrar_solicitacao(form.save(commit=False), request.user)
        messages.success(request, f"Solicitação {solicitacao.codigo} registrada.")
        return redirect("solicitacoes:detalhe", pk=solicitacao.pk)
    return render(request, "solicitacoes/form.html", {"form": form, "titulo": "Nova solicitação"})


@solicitacoes_requerido
def editar(request, pk):
    solicitacao = get_object_or_404(Solicitacao, pk=pk)
    if solicitacao.status not in (Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA):
        messages.error(request, "Só dá para editar solicitações pendentes ou aprovadas.")
        return redirect("solicitacoes:detalhe", pk=pk)
    form = SolicitacaoForm(request.POST or None, instance=solicitacao)
    if request.method == "POST" and form.is_valid():
        form.save()
        solicitacao.registrar(f"Dados alterados por {request.user.nome}.", request.user)
        messages.success(request, "Solicitação atualizada.")
        return redirect("solicitacoes:detalhe", pk=pk)
    return render(request, "solicitacoes/form.html", {"form": form, "titulo": f"Editar {solicitacao.codigo}"})


@solicitacoes_requerido
def detalhe(request, pk):
    solicitacao = get_object_or_404(_base(), pk=pk)
    return render(request, "solicitacoes/detalhe.html", {
        "s": solicitacao,
        "historico": solicitacao.historico.select_related("usuario"),
        "pode_programar": request.user.pode(Modulo.VIAGENS),
    })


def _executar(request, acao, *args):
    try:
        acao(*args, request.user)
    except ValueError as erro:
        messages.error(request, str(erro))
        return False
    return True


@solicitacoes_requerido
@require_POST
def aprovar(request, pk):
    solicitacao = get_object_or_404(Solicitacao, pk=pk)
    if _executar(request, services.aprovar, solicitacao):
        messages.success(request, f"{solicitacao.codigo} aprovada.")
    return voltar(request, "solicitacoes:lista")


@solicitacoes_requerido
@require_POST
def cancelar(request, pk):
    solicitacao = get_object_or_404(Solicitacao, pk=pk)
    if _executar(request, services.cancelar, solicitacao):
        messages.success(request, f"{solicitacao.codigo} cancelada.")
    return redirect("solicitacoes:detalhe", pk=pk)


@solicitacoes_requerido
def recusar(request, pk):
    solicitacao = get_object_or_404(Solicitacao, pk=pk)
    form = MotivoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if _executar(request, services.recusar, solicitacao, form.cleaned_data["motivo"]):
            messages.success(request, f"{solicitacao.codigo} recusada.")
        return redirect("solicitacoes:lista")
    return render(request, "parciais/recusar.html", {
        "form": form,
        "titulo": f"Recusar {solicitacao.codigo}",
        "explicacao": "O motivo fica registrado no histórico e é informado ao paciente.",
        "placeholder": "Ex.: sem vaga nessa data, procure a UBS",
        "voltar": "solicitacoes:lista",
    })
