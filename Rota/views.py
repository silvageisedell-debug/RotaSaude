from django.db import transaction
from django.shortcuts import get_object_or_404, render

from .acesso import exige
from .itinerario import calcular_itinerario
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time

from Veiculo.models import Veiculo

from .forms import ParadaFormSet
from .models import CategoriaRota, Disponibilidade, Parada, Viagem

MSG_HORARIO = "Informe o horário."
MSG_DATA = "A data não pode ser anterior a hoje."
MSG_DATA_AUSENTE = "Informe a data."
MSG_VEICULO = "Selecione um veículo da frota."
MSG_VAGAS = "Informe a quantidade de vagas."


def _formulario(veiculo="", data="", horario="", vagas=""):
    return {
        "veiculo": veiculo,
        "data": data,
        "horario": horario,
        "vagas": vagas,
    }


@exige("admin", "atendente")
def nova_disponibilidade(request):
    veiculos = Veiculo.objects.all()
    contexto = {
        "veiculos": veiculos,
        "erro": None,
        "sucesso": None,
        "form": _formulario(),
    }

    if request.method != "POST":
        return render(request, "Rota/disponibilidade_nova.html", contexto)

    veiculo_id = (request.POST.get("veiculo") or "").strip()
    data_txt = (request.POST.get("data") or "").strip()
    horario_txt = (request.POST.get("horario") or "").strip()
    vagas_txt = (request.POST.get("vagas") or "").strip()
    contexto["form"] = _formulario(veiculo_id, data_txt, horario_txt, vagas_txt)

    if not horario_txt or parse_time(horario_txt) is None:
        contexto["erro"] = MSG_HORARIO
        return render(request, "Rota/disponibilidade_nova.html", contexto)

    data = parse_date(data_txt) if data_txt else None
    if data is None:
        contexto["erro"] = MSG_DATA_AUSENTE
        return render(request, "Rota/disponibilidade_nova.html", contexto)

    if data < timezone.localdate():
        contexto["erro"] = MSG_DATA
        return render(request, "Rota/disponibilidade_nova.html", contexto)

    try:
        veiculo = veiculos.get(pk=int(veiculo_id))
    except (TypeError, ValueError, Veiculo.DoesNotExist):
        contexto["erro"] = MSG_VEICULO
        return render(request, "Rota/disponibilidade_nova.html", contexto)

    try:
        vagas = int(vagas_txt)
    except (TypeError, ValueError):
        contexto["erro"] = MSG_VAGAS
        return render(request, "Rota/disponibilidade_nova.html", contexto)

    if vagas < 0:
        contexto["erro"] = MSG_VAGAS
        return render(request, "Rota/disponibilidade_nova.html", contexto)

    registro = Disponibilidade.objects.create(
        veiculo=veiculo,
        data=data,
        horario=parse_time(horario_txt),
        vagas=vagas,
    )
    contexto["sucesso"] = (
        "Disponibilidade registrada: "
        f"{registro.veiculo}, "
        f"{registro.data.strftime('%d/%m/%Y')}, "
        f"{registro.horario.strftime('%H:%M')}, "
        f"{registro.vagas} vagas."
    )
    return render(request, "Rota/disponibilidade_nova.html", contexto)


MSG_ORIGEM = "Informe a origem."
MSG_DESTINO = "Informe o destino."
MSG_DISPONIBILIDADE = "Selecione uma disponibilidade."
MSG_CATEGORIA = "Selecione uma categoria."
MSG_PARADA = "Informe o local e a ordem de cada parada."
MSG_ORDEM_REPETIDA = "A ordem da parada não pode se repetir na mesma rota."


def _formulario_rota(disponibilidade="", categoria="", origem="", destino=""):
    return {
        "disponibilidade": disponibilidade,
        "categoria": categoria,
        "origem": origem,
        "destino": destino,
    }


def _contexto_rota(viagem, form=None, erro=None, sucesso=None, formset=None, titulo="Nova rota"):
    return {
        "disponibilidades": Disponibilidade.objects.select_related(
            "veiculo", "veiculo__modelo", "veiculo__modelo__marca"
        ),
        "categorias": CategoriaRota.objects.all(),
        "erro": erro,
        "sucesso": sucesso,
        "form": form or _formulario_rota(),
        "formset": formset if formset is not None else _formset_paradas(None, viagem),
        "titulo": titulo,
    }


def _formset_paradas(data, viagem):
    if data is None and viagem.pk:
        initial = [
            {"local": parada.local, "ordem": parada.ordem}
            for parada in viagem.paradas.all()
        ]
        return ParadaFormSet(initial=initial, prefix="paradas")
    if data is None:
        return ParadaFormSet(prefix="paradas")
    return ParadaFormSet(data, prefix="paradas")


def _linhas_paradas(formset):
    if not formset.is_valid():
        return None, MSG_PARADA
    linhas = []
    ordens = []
    for formulario in formset.forms:
        limpo = getattr(formulario, "cleaned_data", None) or {}
        if not limpo:
            continue
        local = (limpo.get("local") or "").strip()
        ordem = limpo.get("ordem")
        if local == "" and ordem is None:
            continue
        if local == "" or ordem is None:
            return None, MSG_PARADA
        linhas.append((local, ordem))
        ordens.append(ordem)
    if len(ordens) != len(set(ordens)):
        return None, MSG_ORDEM_REPETIDA
    return linhas, None


def _gravar_rota(viagem, disponibilidade, categoria, origem, destino, linhas):
    with transaction.atomic():
        viagem.disponibilidade = disponibilidade
        viagem.categoria = categoria
        viagem.origem = origem
        viagem.destino = destino
        viagem.save()
        viagem.paradas.all().delete()
        Parada.objects.bulk_create(
            [
                Parada(viagem=viagem, local=local, ordem=ordem)
                for local, ordem in linhas
            ]
        )
    return viagem


@exige("admin", "atendente")
def lista_rotas(request):
    viagens = list(
        Viagem.objects.select_related(
            "disponibilidade",
            "disponibilidade__veiculo",
            "disponibilidade__veiculo__modelo",
            "disponibilidade__veiculo__modelo__marca",
            "categoria",
        ).prefetch_related("paradas")
    )
    for viagem in viagens:
        viagem.calculo = calcular_itinerario(
            list(viagem.paradas.all()),
            capacidade=viagem.disponibilidade.veiculo.capacidade,
            vagas=viagem.disponibilidade.vagas,
            prioridade=viagem.categoria.prioridade,
        )
    return render(request, "Rota/lista_rotas.html", {"viagens": viagens})


@exige("admin", "atendente")
def nova_rota(request):
    return _tratar_rota(request, Viagem())


@exige("admin", "atendente")
def editar_rota(request, pk):
    viagem = get_object_or_404(Viagem, pk=pk)
    return _tratar_rota(request, viagem)


def _tratar_rota(request, viagem):
    titulo = "Editar rota" if viagem.pk else "Nova rota"
    if request.method != "POST":
        form = _formulario_rota()
        if viagem.pk:
            form = _formulario_rota(
                str(viagem.disponibilidade_id),
                str(viagem.categoria_id),
                viagem.origem,
                viagem.destino,
            )
        return render(
            request,
            "Rota/rota_nova.html",
            _contexto_rota(
                viagem,
                form,
                formset=_formset_paradas(None, viagem),
                titulo=titulo,
            ),
        )

    disponibilidade_id = (request.POST.get("disponibilidade") or "").strip()
    categoria_id = (request.POST.get("categoria") or "").strip()
    origem = (request.POST.get("origem") or "").strip()
    destino = (request.POST.get("destino") or "").strip()
    form = _formulario_rota(disponibilidade_id, categoria_id, origem, destino)
    formset = None
    if "paradas-TOTAL_FORMS" in request.POST:
        formset = _formset_paradas(request.POST, viagem)

    def recusar(mensagem):
        return render(
            request,
            "Rota/rota_nova.html",
            _contexto_rota(
                viagem,
                form,
                erro=mensagem,
                formset=formset,
                titulo=titulo,
            ),
        )

    if not origem:
        return recusar(MSG_ORIGEM)
    if not destino:
        return recusar(MSG_DESTINO)

    try:
        disponibilidade = Disponibilidade.objects.get(pk=int(disponibilidade_id))
    except (TypeError, ValueError, Disponibilidade.DoesNotExist):
        return recusar(MSG_DISPONIBILIDADE)

    try:
        categoria = CategoriaRota.objects.get(pk=int(categoria_id))
    except (TypeError, ValueError, CategoriaRota.DoesNotExist):
        return recusar(MSG_CATEGORIA)

    if formset is None:
        linhas = []
    else:
        linhas, erro_parada = _linhas_paradas(formset)
        if erro_parada:
            return recusar(erro_parada)

    nova = viagem.pk is None
    viagem = _gravar_rota(
        viagem, disponibilidade, categoria, origem, destino, linhas
    )
    sucesso = (
        "Rota publicada: "
        if nova
        else "Rota atualizada: "
    )
    return render(
        request,
        "Rota/rota_nova.html",
        _contexto_rota(
            viagem,
            form,
            sucesso=f"{sucesso}{viagem.origem} → {viagem.destino}, {viagem.categoria}.",
            formset=formset,
            titulo=titulo,
        ),
    )
