from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time

from Veiculo.models import Veiculo

from .models import CategoriaRota, Disponibilidade, Viagem

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


def _formulario_rota(disponibilidade="", categoria="", origem="", destino=""):
    return {
        "disponibilidade": disponibilidade,
        "categoria": categoria,
        "origem": origem,
        "destino": destino,
    }


def _contexto_rota(form=None, erro=None, sucesso=None):
    return {
        "disponibilidades": Disponibilidade.objects.select_related(
            "veiculo", "veiculo__modelo", "veiculo__modelo__marca"
        ),
        "categorias": CategoriaRota.objects.all(),
        "erro": erro,
        "sucesso": sucesso,
        "form": form or _formulario_rota(),
    }


def lista_rotas(request):
    viagens = Viagem.objects.select_related(
        "disponibilidade",
        "disponibilidade__veiculo",
        "disponibilidade__veiculo__modelo",
        "disponibilidade__veiculo__modelo__marca",
        "categoria",
    )
    return render(request, "Rota/lista_rotas.html", {"viagens": viagens})


def nova_rota(request):
    if request.method != "POST":
        return render(request, "Rota/rota_nova.html", _contexto_rota())

    disponibilidade_id = (request.POST.get("disponibilidade") or "").strip()
    categoria_id = (request.POST.get("categoria") or "").strip()
    origem = (request.POST.get("origem") or "").strip()
    destino = (request.POST.get("destino") or "").strip()
    form = _formulario_rota(disponibilidade_id, categoria_id, origem, destino)

    if not origem:
        return render(
            request,
            "Rota/rota_nova.html",
            _contexto_rota(form, erro=MSG_ORIGEM),
        )

    if not destino:
        return render(
            request,
            "Rota/rota_nova.html",
            _contexto_rota(form, erro=MSG_DESTINO),
        )

    try:
        disponibilidade = Disponibilidade.objects.get(pk=int(disponibilidade_id))
    except (TypeError, ValueError, Disponibilidade.DoesNotExist):
        return render(
            request,
            "Rota/rota_nova.html",
            _contexto_rota(form, erro=MSG_DISPONIBILIDADE),
        )

    try:
        categoria = CategoriaRota.objects.get(pk=int(categoria_id))
    except (TypeError, ValueError, CategoriaRota.DoesNotExist):
        return render(
            request,
            "Rota/rota_nova.html",
            _contexto_rota(form, erro=MSG_CATEGORIA),
        )

    viagem = Viagem.objects.create(
        disponibilidade=disponibilidade,
        categoria=categoria,
        origem=origem,
        destino=destino,
    )
    return render(
        request,
        "Rota/rota_nova.html",
        _contexto_rota(
            form,
            sucesso=(
                "Rota publicada: "
                f"{viagem.origem} → {viagem.destino}, "
                f"{viagem.categoria}."
            ),
        ),
    )
