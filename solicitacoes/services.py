from django.db import transaction

from .models import Solicitacao


@transaction.atomic
def registrar_solicitacao(solicitacao, usuario):
    solicitacao.criado_por = usuario
    solicitacao.status = Solicitacao.Status.PENDENTE
    solicitacao.save()
    solicitacao.registrar(f"Registrada pelo atendimento ({usuario.nome}).", usuario)
    return solicitacao


def _exigir(solicitacao, *permitidos):
    if solicitacao.status not in permitidos:
        raise ValueError(f"{solicitacao.codigo} está {solicitacao.get_status_display().lower()} e não pode mudar assim.")


@transaction.atomic
def aprovar(solicitacao, usuario):
    _exigir(solicitacao, Solicitacao.Status.PENDENTE)
    solicitacao.status = Solicitacao.Status.APROVADA
    solicitacao.save(update_fields=["status"])
    solicitacao.registrar(f"Aprovada por {usuario.nome}. Aguardando programação da viagem.", usuario)


@transaction.atomic
def recusar(solicitacao, motivo, usuario):
    _exigir(solicitacao, Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA)
    solicitacao.status = Solicitacao.Status.NEGADA
    solicitacao.motivo_recusa = motivo
    solicitacao.save(update_fields=["status", "motivo_recusa"])
    solicitacao.registrar(f"Recusada por {usuario.nome}: {motivo}", usuario)


@transaction.atomic
def cancelar(solicitacao, usuario):
    _exigir(solicitacao, Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA)
    solicitacao.status = Solicitacao.Status.CANCELADA
    solicitacao.save(update_fields=["status"])
    solicitacao.registrar(f"Cancelada por {usuario.nome}.", usuario)
