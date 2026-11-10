from django.db import transaction
from django.db.models import ProtectedError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from contas.api_permissoes import PermissaoFrota, PermissaoSolicitacoes
from portal.api_base import salvar_formulario
from portal.forms import MotivoForm

from .forms import MotoristaForm, PedidoPontoForm, PontoEmbarqueForm
from .models import Modelo, Motorista, PedidoPontoEmbarque, PontoEmbarque, Veiculo
from .serializers import ModeloSerializer, MotoristaSerializer, PedidoPontoSerializer, PontoEmbarqueSerializer, VeiculoSerializer


@method_decorator(csrf_exempt, name="dispatch")
class ModeloViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Modelo.objects.select_related("marca")
    serializer_class = ModeloSerializer
    permission_classes = [PermissaoFrota]


@method_decorator(csrf_exempt, name="dispatch")
class VeiculoViewSet(viewsets.ModelViewSet):
    queryset = Veiculo.objects.select_related("modelo__marca")
    serializer_class = VeiculoSerializer
    permission_classes = [PermissaoFrota]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def destroy(self, request, *args, **kwargs):
        veiculo = self.get_object()
        try:
            veiculo.delete()
        except ProtectedError:
            return Response(
                {"detail": "Este veículo já tem viagens registradas e não pode ser apagado."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def status(self, request, pk=None):
        veiculo = self.get_object()
        novo = request.data.get("status")
        if novo not in Veiculo.Status.values:
            return Response({"detail": "Status inválido."}, status=status.HTTP_400_BAD_REQUEST)
        veiculo.status = novo
        veiculo.save(update_fields=["status"])
        return Response(self.get_serializer(veiculo).data)


@method_decorator(csrf_exempt, name="dispatch")
class MotoristaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                       mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Motorista.objects.filter(ativo=True)
    serializer_class = MotoristaSerializer
    permission_classes = [PermissaoFrota]

    def create(self, request, *args, **kwargs):
        motorista = salvar_formulario(MotoristaForm, request.data)
        return Response(self.get_serializer(motorista).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        motorista = salvar_formulario(MotoristaForm, request.data, instance=self.get_object())
        return Response(self.get_serializer(motorista).data)


@method_decorator(csrf_exempt, name="dispatch")
class PontoEmbarqueViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                           mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = PontoEmbarque.objects.filter(ativo=True)
    serializer_class = PontoEmbarqueSerializer
    permission_classes = [PermissaoFrota]

    def create(self, request, *args, **kwargs):
        ponto = salvar_formulario(PontoEmbarqueForm, request.data)
        return Response(self.get_serializer(ponto).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        ponto = salvar_formulario(PontoEmbarqueForm, request.data, instance=self.get_object())
        return Response(self.get_serializer(ponto).data)

    def destroy(self, request, *args, **kwargs):
        if PontoEmbarque.objects.filter(ativo=True).count() <= 1:
            return Response({"detail": "Mantenha pelo menos um ponto de embarque."}, status=status.HTTP_400_BAD_REQUEST)
        ponto = self.get_object()
        ponto.ativo = False
        ponto.save(update_fields=["ativo"])
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_exempt, name="dispatch")
class PedidoPontoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = PedidoPontoEmbarque.objects.select_related("solicitante")
    serializer_class = PedidoPontoSerializer

    def get_permissions(self):
        if self.action == "create":
            return [PermissaoSolicitacoes()]
        return [PermissaoFrota()]

    def create(self, request, *args, **kwargs):
        formulario = PedidoPontoForm(request.data)
        if not formulario.is_valid():
            return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
        pedido = formulario.save(commit=False)
        pedido.solicitante = request.user
        pedido.save()
        return Response(self.get_serializer(pedido).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def aprovar(self, request, pk=None):
        pedido = self.get_object()
        if pedido.status != PedidoPontoEmbarque.Status.PENDENTE:
            return Response({"detail": "Este pedido já foi respondido."}, status=status.HTTP_400_BAD_REQUEST)
        formulario = PontoEmbarqueForm({"nome": pedido.nome, "endereco": pedido.endereco, "cep": pedido.cep})
        if not formulario.is_valid():
            return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            formulario.save()
            pedido.status = PedidoPontoEmbarque.Status.APROVADO
            pedido.respondido_por = request.user
            pedido.save(update_fields=["status", "respondido_por"])
        return Response(self.get_serializer(pedido).data)

    @action(detail=True, methods=["post"])
    def recusar(self, request, pk=None):
        pedido = self.get_object()
        if pedido.status != PedidoPontoEmbarque.Status.PENDENTE:
            return Response({"detail": "Este pedido já foi respondido."}, status=status.HTTP_400_BAD_REQUEST)
        formulario = MotivoForm(request.data)
        if not formulario.is_valid():
            return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
        pedido.status = PedidoPontoEmbarque.Status.RECUSADO
        pedido.motivo_recusa = formulario.cleaned_data["motivo"]
        pedido.respondido_por = request.user
        pedido.save(update_fields=["status", "motivo_recusa", "respondido_por"])
        return Response(self.get_serializer(pedido).data)
