"""
Regras da operação de viagens: disponibilidade calculada, programação e execução.

A disponibilidade não é cadastrada à mão: sai do status do veículo, da validade
da CNH do motorista e das viagens ativas que se sobrepõem ao horário pedido.
"""

from dataclasses import dataclass, field

from django.db import transaction
from django.utils import timezone

from frota.models import Motorista, Veiculo
from solicitacoes.models import Solicitacao

from .models import HORA_FIM, HORA_INICIO, Parada, Viagem

DISPONIVEL = "Disponível"
PROGRAMADO = "Programado"
EM_VIAGEM = "Em viagem"
MANUTENCAO = "Manutenção"
OCUPADO = "Ocupado"
CNH_VENCIDA = "CNH vencida"


@dataclass
class Situacao:
    objeto: object
    status: str
    detalhe: str = ""
    viagens: list = field(default_factory=list)

    @property
    def livre(self):
        return self.status == DISPONIVEL


def _faixa(viagem):
    return f"{viagem.saida:%H:%M} às {viagem.chegada:%H:%M}"


def _sobrepoe(inicio, fim, viagem):
    return inicio < viagem.fim_minutos and viagem.inicio_minutos < fim


def viagens_ativas(data, excluir=None):
    qs = Viagem.objects.filter(data=data, status__in=Viagem.ATIVAS).select_related("veiculo", "motorista")
    if excluir is not None:
        qs = qs.exclude(pk=excluir.pk)
    return list(qs)


def disponibilidade(data, saida=None, duracao_horas=None, excluir=None):
    """
    Situação de cada veículo e motorista.

    Sem horário: visão do dia (Disponível, Programado, Em viagem, Manutenção, CNH vencida).
    Com horário: visão da janela pedida (Disponível, Ocupado, Em viagem, Manutenção, CNH vencida).
    """
    ativas = viagens_ativas(data, excluir)
    hoje = data == timezone.localdate()
    janela = None
    if saida is not None and duracao_horas:
        inicio = saida.hour * 60 + saida.minute
        janela = (inicio, inicio + duracao_horas * 60)

    veiculos = []
    for veiculo in Veiculo.objects.select_related("modelo__marca"):
        do_veiculo = [v for v in ativas if v.veiculo_id == veiculo.pk]
        rodando_sem_viagem = hoje and veiculo.status == Veiculo.Status.EM_VIAGEM and not do_veiculo
        if janela:
            conflito = [v for v in do_veiculo if _sobrepoe(*janela, v)]
            if veiculo.em_manutencao:
                status = MANUTENCAO
            elif conflito:
                status = OCUPADO
            elif rodando_sem_viagem:
                status = EM_VIAGEM
            else:
                status = DISPONIVEL
            detalhe = f"ocupado {_faixa(conflito[0])}" if conflito else ""
        else:
            andando = any(v.status == Viagem.Status.EM_ANDAMENTO for v in do_veiculo) or rodando_sem_viagem
            if veiculo.em_manutencao:
                status = MANUTENCAO
            elif andando:
                status = EM_VIAGEM
            elif do_veiculo:
                status = PROGRAMADO
            else:
                status = DISPONIVEL
            detalhe = ", ".join(_faixa(v) for v in do_veiculo)
        veiculos.append(Situacao(veiculo, status, detalhe, do_veiculo))

    motoristas = []
    for motorista in Motorista.objects.filter(ativo=True):
        do_motorista = [v for v in ativas if v.motorista_id == motorista.pk]
        cnh_ok = motorista.cnh_valida(data)
        if janela:
            conflito = [v for v in do_motorista if _sobrepoe(*janela, v)]
            status = CNH_VENCIDA if not cnh_ok else OCUPADO if conflito else DISPONIVEL
            detalhe = f"ocupado {_faixa(conflito[0])}" if conflito else "Sem viagem nesse horário"
        else:
            andando = any(v.status == Viagem.Status.EM_ANDAMENTO for v in do_motorista)
            status = CNH_VENCIDA if not cnh_ok else EM_VIAGEM if andando else PROGRAMADO if do_motorista else DISPONIVEL
            detalhe = ", ".join(_faixa(v) for v in do_motorista) or "Sem viagens neste dia"
        motoristas.append(Situacao(motorista, status, detalhe, do_motorista))

    return {"veiculos": veiculos, "motoristas": motoristas}


def validar_programacao(data, saida, duracao_horas, veiculo, motorista, solicitacoes, excluir=None):
    """Devolve a lista de motivos que impedem a viagem. Lista vazia: pode programar."""
    erros = []
    if not solicitacoes:
        erros.append("Marque ao menos um paciente.")
    if data < timezone.localdate():
        erros.append("A data da viagem não pode ser anterior a hoje.")
    inicio = saida.hour * 60 + saida.minute
    fim = inicio + duracao_horas * 60
    if not 1 <= duracao_horas <= 12:
        erros.append("A viagem precisa durar de 1 a 12 horas.")
    if inicio < HORA_INICIO * 60 or fim > HORA_FIM * 60:
        erros.append(f"A viagem precisa sair a partir das {HORA_INICIO:02d}h e terminar até as {HORA_FIM}h.")
    if veiculo.em_manutencao:
        erros.append("Este veículo está em manutenção.")
    if not motorista.cnh_valida(data):
        erros.append("A CNH deste motorista está vencida na data da viagem.")

    for s in solicitacoes:
        if s.status not in (Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA):
            erros.append(f"{s.codigo} não está aguardando viagem (status {s.get_status_display().lower()}).")
        elif s.data != data:
            erros.append(f"{s.codigo} é para {s.data:%d/%m/%Y}. Programe a viagem nessa data.")

    lugares = sum(s.lugares for s in solicitacoes)
    if lugares > veiculo.capacidade:
        erros.append(f"Passageiros ({lugares}) acima da capacidade do veículo ({veiculo.capacidade}).")

    for v in viagens_ativas(data, excluir):
        if (v.veiculo_id == veiculo.pk or v.motorista_id == motorista.pk) and _sobrepoe(inicio, fim, v):
            quem = "veículo" if v.veiculo_id == veiculo.pk else "motorista"
            erros.append(f"Conflito: o {quem} já tem a viagem {v.codigo} das {_faixa(v)}.")
            break
    return erros


def _resumo_destino(solicitacoes):
    nomes = []
    for s in solicitacoes:
        nome = str(s.destino)
        if nome not in nomes:
            nomes.append(nome)
    return " / ".join(nomes)[:250]


def _montar_itinerario(viagem, solicitacoes):
    """Embarques pela ordem do horário dos pacientes e, no fim, os destinos."""
    locais = []
    for s in sorted(solicitacoes, key=lambda s: (s.horario, s.pk)):
        if s.ponto_embarque.nome not in locais:
            locais.append(s.ponto_embarque.nome)
    for s in solicitacoes:
        if str(s.destino) not in locais:
            locais.append(str(s.destino))
    Parada.objects.bulk_create(
        Parada(viagem=viagem, ordem=i, local=local[:120]) for i, local in enumerate(locais, start=1)
    )


@transaction.atomic
def programar_viagem(*, data, saida, duracao_horas, veiculo, motorista, solicitacoes, usuario):
    solicitacoes = list(
        Solicitacao.objects.select_for_update()
        .select_related("destino", "ponto_embarque")
        .filter(pk__in=[s.pk for s in solicitacoes])
    )
    erros = validar_programacao(data, saida, duracao_horas, veiculo, motorista, solicitacoes)
    if erros:
        raise ValueError(erros)
    viagem = Viagem.objects.create(
        veiculo=veiculo,
        motorista=motorista,
        data=data,
        saida=saida,
        duracao_horas=duracao_horas,
        destino=_resumo_destino(solicitacoes),
        criado_por=usuario,
    )
    _montar_itinerario(viagem, solicitacoes)
    for s in solicitacoes:
        s.status = Solicitacao.Status.AGENDADA
        s.viagem = viagem
        s.embarcou = False
        s.save(update_fields=["status", "viagem", "embarcou"])
        s.registrar(
            f"Aceita por {usuario.nome}. Veículo {veiculo}, motorista {motorista}, "
            f"saída às {saida:%H:%M} em {data:%d/%m/%Y} ({viagem.codigo}).",
            usuario,
        )
    return viagem


@transaction.atomic
def iniciar_viagem(viagem, usuario):
    if viagem.status != Viagem.Status.PROGRAMADA:
        raise ValueError(["Só uma viagem programada pode ser iniciada."])
    viagem.status = Viagem.Status.EM_ANDAMENTO
    viagem.save(update_fields=["status"])
    for s in viagem.passageiros.all():
        s.status = Solicitacao.Status.EM_VIAGEM
        s.save(update_fields=["status"])
        s.registrar("Viagem iniciada.", usuario)
    Veiculo.objects.filter(pk=viagem.veiculo_id).update(status=Veiculo.Status.EM_VIAGEM)


def alternar_embarque(viagem, solicitacao):
    if viagem.status != Viagem.Status.EM_ANDAMENTO or solicitacao.viagem_id != viagem.pk:
        raise ValueError(["Marque o embarque só com a viagem em andamento."])
    solicitacao.embarcou = not solicitacao.embarcou
    solicitacao.save(update_fields=["embarcou"])
    return solicitacao.embarcou


@transaction.atomic
def concluir_viagem(viagem, usuario):
    """Quem embarcou conclui; quem não embarcou volta para a regulação como aprovada."""
    if viagem.status != Viagem.Status.EM_ANDAMENTO:
        raise ValueError(["Só uma viagem em andamento pode ser concluída."])
    viagem.status = Viagem.Status.CONCLUIDA
    viagem.save(update_fields=["status"])
    for s in viagem.passageiros.all():
        if s.embarcou:
            s.status = Solicitacao.Status.CONCLUIDA
            s.save(update_fields=["status"])
            s.registrar("Viagem concluída.", usuario)
        else:
            s.status = Solicitacao.Status.APROVADA
            s.viagem = None
            s.save(update_fields=["status", "viagem"])
            s.registrar("Não embarcou. Voltou para a regulação.", usuario)
    Veiculo.objects.filter(pk=viagem.veiculo_id).update(status=Veiculo.Status.DISPONIVEL)


@transaction.atomic
def cancelar_viagem(viagem, usuario):
    if viagem.status != Viagem.Status.PROGRAMADA:
        raise ValueError(["Só uma viagem programada pode ser cancelada."])
    viagem.status = Viagem.Status.CANCELADA
    viagem.save(update_fields=["status"])
    for s in viagem.passageiros.all():
        s.status = Solicitacao.Status.APROVADA
        s.viagem = None
        s.save(update_fields=["status", "viagem"])
        s.registrar(f"Viagem {viagem.codigo} cancelada pela regulação. Aguardando novo veículo.", usuario)
