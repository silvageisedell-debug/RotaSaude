from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from contas.api_permissoes import PermissaoSolicitacoes
from portal.api_base import resposta_regra, salvar_formulario
from portal.forms import MotivoForm

from . import services
from .forms import SolicitacaoForm
from .models import Categoria, Destino, Solicitacao
from .serializers import CategoriaSerializer, DestinoSerializer, SolicitacaoDetalheSerializer, SolicitacaoSerializer


def _base():
    return Solicitacao.objects.select_related("destino", "ponto_embarque", "categoria", "viagem")


@method_decorator(csrf_exempt, name="dispatch")
class CategoriaViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [PermissaoSolicitacoes]


@method_decorator(csrf_exempt, name="dispatch")
class DestinoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Destino.objects.filter(ativo=True)
    serializer_class = DestinoSerializer
    permission_classes = [PermissaoSolicitacoes]


@method_decorator(csrf_exempt, name="dispatch")
class SolicitacaoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                         mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = _base()
    permission_classes = [PermissaoSolicitacoes]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SolicitacaoDetalheSerializer
        return SolicitacaoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_filtro = self.request.query_params.get("status", "")
        busca = self.request.query_params.get("q", "").strip()
        if status_filtro in Solicitacao.Status.values:
            qs = qs.filter(status=status_filtro)
        if busca:
            filtro = Q(paciente__icontains=busca) | Q(destino__nome__icontains=busca) | Q(destino__cidade__icontains=busca)
            codigo = busca.upper().removeprefix("SOL-")
            if codigo.isdigit():
                filtro |= Q(pk=int(codigo))
            qs = qs.filter(filtro)
        if self.action == "retrieve":
            qs = qs.prefetch_related("historico__usuario")
        return qs

    def create(self, request, *args, **kwargs):
        formulario = SolicitacaoForm(request.data)
        if not formulario.is_valid():
            return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
        solicitacao = services.registrar_solicitacao(formulario.save(commit=False), request.user)
        return Response(self.get_serializer(solicitacao).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        solicitacao = self.get_object()
        if solicitacao.status not in (Solicitacao.Status.PENDENTE, Solicitacao.Status.APROVADA):
            return Response({"detail": "Só dá para editar solicitações pendentes ou aprovadas."}, status=status.HTTP_400_BAD_REQUEST)
        solicitacao = salvar_formulario(SolicitacaoForm, request.data, instance=solicitacao)
        solicitacao.registrar(f"Dados alterados por {request.user.nome}.", request.user)
        return Response(self.get_serializer(solicitacao).data)

    def _acao(self, solicitacao, funcao):
        try:
            funcao()
        except ValueError as erro:
            return resposta_regra(erro)
        solicitacao.refresh_from_db()
        return Response(self.get_serializer(solicitacao).data)

    @action(detail=True, methods=["post"])
    def aprovar(self, request, pk=None):
        solicitacao = self.get_object()
        return self._acao(solicitacao, lambda: services.aprovar(solicitacao, request.user))

    @action(detail=True, methods=["post"])
    def recusar(self, request, pk=None):
        solicitacao = self.get_object()
        formulario = MotivoForm(request.data)
        if not formulario.is_valid():
            return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
        return self._acao(
            solicitacao,
            lambda: services.recusar(solicitacao, formulario.cleaned_data["motivo"], request.user),
        )

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        solicitacao = self.get_object()
        return self._acao(solicitacao, lambda: services.cancelar(solicitacao, request.user))
