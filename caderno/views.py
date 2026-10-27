from datetime import datetime, time, timedelta

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from contas.models import Modulo
from contas.permissoes import modulo_requerido
from portal.navegacao import voltar

from .forms import AnotacaoForm
from .models import Anotacao

caderno_requerido = modulo_requerido(Modulo.CADERNO)

FILTROS = [("todas", "Todas"), ("lembretes", "Lembretes"), ("fixadas", "Fixadas"), ("concluidas", "Concluídas")]


def _minha(request, pk):
    return get_object_or_404(Anotacao, pk=pk, usuario=request.user)


@caderno_requerido
def inicio(request):
    edicao = None
    if request.GET.get("editar", "").isdigit():
        edicao = Anotacao.objects.filter(pk=int(request.GET["editar"]), usuario=request.user).first()
    form = AnotacaoForm(request.POST or None, instance=edicao)
    if request.method == "POST":
        edicao_pk = request.POST.get("editar", "")
        if edicao_pk.isdigit():
            edicao = _minha(request, int(edicao_pk))
            form = AnotacaoForm(request.POST, instance=edicao)
        if form.is_valid():
            anotacao = form.save(commit=False)
            anotacao.usuario = request.user
            anotacao.save()
            if edicao:
                messages.success(request, "Anotação atualizada.")
            elif anotacao.lembrar_em:
                messages.success(request, "Anotação salva. Eu te lembro na hora marcada.")
            else:
                messages.success(request, "Anotação salva.")
            return redirect("caderno:inicio")

    filtro = request.GET.get("f", "todas")
    busca = request.GET.get("q", "").strip()
    qs = Anotacao.objects.filter(usuario=request.user, concluida=(filtro == "concluidas"))
    if filtro == "lembretes":
        qs = qs.exclude(lembrar_em=None)
    elif filtro == "fixadas":
        qs = qs.filter(fixada=True)
    if busca:
        qs = qs.filter(Q(titulo__icontains=busca) | Q(texto__icontains=busca))

    agora = timezone.localtime()
    return render(request, "caderno/inicio.html", {
        "form": form,
        "edicao": edicao,
        "anotacoes": qs,
        "filtro": filtro,
        "filtros": FILTROS,
        "busca": busca,
        "cores": list(enumerate(Anotacao.CORES)),
        "cor_atual": int(form["cor"].value() or 0),
        "fixada_atual": str(form["fixada"].value()) in ("True", "true", "on", "1"),
        "agora": agora.strftime("%Y-%m-%dT%H:%M"),
        "em_1_hora": (agora + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M"),
        "amanha_8h": datetime.combine(agora.date() + timedelta(days=1), time(8, 0)).strftime("%Y-%m-%dT%H:%M"),
    })


@caderno_requerido
@require_POST
def concluir(request, pk):
    anotacao = _minha(request, pk)
    anotacao.concluida = not anotacao.concluida
    anotacao.save(update_fields=["concluida"])
    return voltar(request, "caderno:inicio")


@caderno_requerido
@require_POST
def apagar(request, pk):
    _minha(request, pk).delete()
    messages.success(request, "Anotação apagada.")
    return redirect("caderno:inicio")


@caderno_requerido
@require_POST
def adiar(request, pk):
    anotacao = _minha(request, pk)
    try:
        minutos = int(request.POST.get("minutos", "15"))
    except ValueError:
        minutos = 15
    if minutos == 1440:
        amanha = timezone.localdate() + timedelta(days=1)
        anotacao.lembrar_em = timezone.make_aware(datetime.combine(amanha, time(8, 0)))
    else:
        anotacao.lembrar_em = timezone.now() + timedelta(minutes=max(1, minutos))
    anotacao.avisado_para = None
    anotacao.save(update_fields=["lembrar_em", "avisado_para"])
    return voltar(request, "caderno:inicio")


@caderno_requerido
@require_POST
def avisado(request):
    """Fecha o aviso de lembretes: marca os vencidos como já mostrados."""
    for anotacao in Anotacao.vencidas_de(request.user):
        anotacao.avisado_para = anotacao.lembrar_em
        anotacao.save(update_fields=["avisado_para"])
    return voltar(request, "caderno:inicio")
