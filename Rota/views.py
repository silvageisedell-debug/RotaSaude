from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time

from Veiculo.models import Veiculo

from .models import Disponibilidade

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
