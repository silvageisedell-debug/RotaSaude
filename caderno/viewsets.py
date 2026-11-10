from datetime import datetime, time, timedelta

from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from contas.api_permissoes import PermissaoCaderno
from .forms import AnotacaoForm
from .models import Anotacao
from .serializers import AnotacaoSerializer


@method_decorator(csrf_exempt, name="dispatch")
class AnotacaoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                      mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = AnotacaoSerializer
    permission_classes = [PermissaoCaderno]

    def get_queryset(self):
        filtro = self.request.query_params.get("f", "todas")
        busca = self.request.query_params.get("q", "").strip()
        qs = Anotacao.objects.filter(usuario=self.request.user, concluida=(filtro == "concluidas"))
        if filtro == "lembretes":
            qs = qs.exclude(lembrar_em=None)
        elif filtro == "fixadas":
            qs = qs.filter(fixada=True)
        if busca:
            qs = qs.filter(Q(titulo__icontains=busca) | Q(texto__icontains=busca))
        return qs

    def _gravar(self, request, instance=None):
        formulario = AnotacaoForm(request.data, instance=instance)
        if not formulario.is_valid():
            return None, Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
        anotacao = formulario.save(commit=False)
        anotacao.usuario = request.user
        anotacao.save()
        return anotacao, None

    def create(self, request, *args, **kwargs):
        anotacao, erro = self._gravar(request)
        if erro:
            return erro
        return Response(self.get_serializer(anotacao).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        anotacao, erro = self._gravar(request, instance=self.get_object())
        if erro:
            return erro
        return Response(self.get_serializer(anotacao).data)

    @action(detail=True, methods=["post"])
    def concluir(self, request, pk=None):
        anotacao = self.get_object()
        anotacao.concluida = not anotacao.concluida
        anotacao.save(update_fields=["concluida"])
        return Response(self.get_serializer(anotacao).data)

    @action(detail=True, methods=["post"])
    def adiar(self, request, pk=None):
        anotacao = self.get_object()
        try:
            minutos = int(request.data.get("minutos", 15))
        except (TypeError, ValueError):
            minutos = 15
        if minutos == 1440:
            amanha = timezone.localdate() + timedelta(days=1)
            anotacao.lembrar_em = timezone.make_aware(datetime.combine(amanha, time(8, 0)))
        else:
            anotacao.lembrar_em = timezone.now() + timedelta(minutes=max(1, minutos))
        anotacao.avisado_para = None
        anotacao.save(update_fields=["lembrar_em", "avisado_para"])
        return Response(self.get_serializer(anotacao).data)

    @action(detail=False, methods=["post"])
    def avisado(self, request):
        for anotacao in Anotacao.vencidas_de(request.user):
            anotacao.avisado_para = anotacao.lembrar_em
            anotacao.save(update_fields=["avisado_para"])
        return Response(status=status.HTTP_204_NO_CONTENT)
