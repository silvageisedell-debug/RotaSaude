from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.response import Response

from contas.api_permissoes import PermissaoInicio
from frota.models import Veiculo
from solicitacoes.models import HistoricoSolicitacao, Solicitacao
from viagens.models import Viagem
from viagens.services import disponibilidade

from painel.views import CORES_STATUS


def _situacao(item, nome, info):
    return {"id": item.objeto.pk, "nome": nome, "info": info, "status": item.status, "livre": item.livre}


@method_decorator(csrf_exempt, name="dispatch")
class InicioViewSet(viewsets.ViewSet):
    permission_classes = [PermissaoInicio]

    def list(self, request):
        hoje = timezone.localdate()
        contagem = {s: Solicitacao.objects.filter(status=s).count() for s in Solicitacao.FLUXO}
        viagens_hoje = (
            Viagem.objects.filter(data=hoje).exclude(status=Viagem.Status.CANCELADA)
            .select_related("veiculo__modelo__marca", "motorista")
        )
        acao = Solicitacao.objects.filter(
            status__in=[Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA]
        ).select_related("destino", "categoria")
        situacao = disponibilidade(hoje)
        return Response({
            "hoje": hoje.isoformat(),
            "kpi_pendentes": contagem[Solicitacao.Status.PENDENTE],
            "kpi_viagens_hoje": viagens_hoje.count(),
            "kpi_veiculos": Veiculo.objects.filter(status=Veiculo.Status.DISPONIVEL).count(),
            "kpi_concluidas": contagem[Solicitacao.Status.CONCLUIDA],
            "grafico": {
                "rotulos": [s.label for s in Solicitacao.FLUXO],
                "valores": [contagem[s] for s in Solicitacao.FLUXO],
                "cores": [CORES_STATUS[s] for s in Solicitacao.FLUXO],
            },
            "viagens_hoje": [
                {"id": v.pk, "codigo": v.codigo, "destino": v.destino, "saida": f"{v.saida:%H:%M}", "status": v.status}
                for v in viagens_hoje
            ],
            "precisam_acao": [
                {"id": s.pk, "codigo": s.codigo, "paciente": s.paciente, "status": s.status, "destino": str(s.destino)}
                for s in acao
            ],
            "disponibilidade": {
                "veiculos": [_situacao(s, str(s.objeto.modelo), s.objeto.placa_formatada) for s in situacao["veiculos"]],
                "motoristas": [_situacao(s, s.objeto.nome, s.detalhe) for s in situacao["motoristas"]],
            },
        })


@method_decorator(csrf_exempt, name="dispatch")
class ResumoViewSet(viewsets.ViewSet):
    permission_classes = [PermissaoInicio]

    def list(self, request):
        hoje = timezone.localdate()
        pendentes = Solicitacao.objects.filter(
            status__in=[Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA]
        ).select_related("destino")
        viagens = Viagem.objects.filter(data=hoje, status__in=Viagem.ATIVAS).select_related("veiculo", "motorista")
        acoes = HistoricoSolicitacao.objects.filter(usuario=request.user).select_related("solicitacao")[:6]
        return Response({
            "pendentes": [
                {"id": s.pk, "codigo": s.codigo, "paciente": s.paciente, "destino": str(s.destino), "status": s.status}
                for s in pendentes
            ],
            "viagens": [
                {"id": v.pk, "codigo": v.codigo, "destino": v.destino, "saida": f"{v.saida:%H:%M}", "status": v.status}
                for v in viagens
            ],
            "acoes": [{"texto": a.texto, "criado_em": a.criado_em} for a in acoes],
        })
