from django.utils.dateparse import parse_date, parse_time
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from contas.api_permissoes import PermissaoViagens
from portal.api_base import resposta_regra
from solicitacoes.models import Solicitacao

from . import services
from .forms import ProgramarViagemForm
from .models import Viagem
from .serializers import ViagemDetalheSerializer, ViagemSerializer


def _linha(situacao, nome, info):
    return {"id": situacao.objeto.pk, "nome": nome, "info": info, "status": situacao.status, "livre": situacao.livre}


@method_decorator(csrf_exempt, name="dispatch")
class ViagemViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [PermissaoViagens]

    def get_queryset(self):
        qs = Viagem.objects.select_related("veiculo__modelo__marca", "motorista")
        dia = parse_date(self.request.query_params.get("data") or "")
        if self.action == "list":
            qs = qs.filter(data=dia or timezone.localdate()).exclude(status=Viagem.Status.CANCELADA)
        if self.action == "retrieve":
            qs = qs.prefetch_related("passageiros", "paradas")
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ViagemDetalheSerializer
        return ViagemSerializer

    def create(self, request, *args, **kwargs):
        formulario = ProgramarViagemForm(request.data)
        if not formulario.is_valid():
            return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
        dados = formulario.cleaned_data
        try:
            viagem = services.programar_viagem(
                data=dados["data"], saida=dados["saida"], duracao_horas=dados["duracao_horas"],
                veiculo=dados["veiculo"], motorista=dados["motorista"],
                solicitacoes=list(dados["solicitacoes"]), usuario=request.user,
            )
        except ValueError as erro:
            return resposta_regra(erro)
        return Response(ViagemDetalheSerializer(viagem).data, status=status.HTTP_201_CREATED)

    def _acao(self, funcao, sucesso):
        viagem = self.get_object()
        try:
            funcao(viagem, self.request.user)
        except ValueError as erro:
            return resposta_regra(erro)
        viagem.refresh_from_db()
        return Response(self.get_serializer(viagem).data)

    @action(detail=False, methods=["get"])
    def disponibilidade(self, request):
        dia = parse_date(request.query_params.get("data") or "") or timezone.localdate()
        saida = parse_time(request.query_params.get("saida") or "")
        try:
            duracao = max(1, min(12, int(request.query_params.get("duracao", "1"))))
        except ValueError:
            duracao = 1
        situacao = services.disponibilidade(dia, saida, duracao)
        return Response({
            "veiculos": [
                _linha(s, str(s.objeto.modelo), f"{s.objeto.placa_formatada} · {s.objeto.capacidade} lugares"
                       + (f" · {s.detalhe}" if s.detalhe else ""))
                for s in situacao["veiculos"]
            ],
            "motoristas": [_linha(s, s.objeto.nome, s.detalhe) for s in situacao["motoristas"]],
        })

    @action(detail=True, methods=["post"])
    def iniciar(self, request, pk=None):
        return self._acao(services.iniciar_viagem, "iniciada")

    @action(detail=True, methods=["post"])
    def concluir(self, request, pk=None):
        return self._acao(services.concluir_viagem, "concluida")

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        return self._acao(services.cancelar_viagem, "cancelada")

    @action(detail=True, methods=["post"])
    def embarque(self, request, pk=None):
        viagem = self.get_object()
        solicitacao = Solicitacao.objects.filter(pk=request.data.get("solicitacao"), viagem=viagem).first()
        if solicitacao is None:
            return Response({"detail": "Passageiro não encontrado nesta viagem."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            embarcou = services.alternar_embarque(viagem, solicitacao)
        except ValueError as erro:
            return resposta_regra(erro)
        return Response({"solicitacao": solicitacao.pk, "paciente": solicitacao.paciente, "embarcou": embarcou})
