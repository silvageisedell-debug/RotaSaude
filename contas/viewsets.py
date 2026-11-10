from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from portal.api_base import salvar_formulario

from .api_permissoes import PermissaoAdmin
from .forms import CadastroUsuarioForm, LoginForm
from .models import MODULOS_CONFIGURAVEIS, PERFIS_CONFIGURAVEIS, Modulo, PermissaoModulo, Usuario
from .serializers import UsuarioSerializer


@method_decorator(csrf_exempt, name="dispatch")
class EntrarView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        formulario = LoginForm(request.data, request=request._request)
        if not formulario.is_valid():
            return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=formulario.usuario)
        return Response({"token": token.key, "usuario": UsuarioSerializer(formulario.usuario).data})


@method_decorator(csrf_exempt, name="dispatch")
class SairView(APIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_exempt, name="dispatch")
class UsuarioViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Usuario.objects.order_by("nome")
    serializer_class = UsuarioSerializer
    permission_classes = [PermissaoAdmin]

    def create(self, request, *args, **kwargs):
        usuario = salvar_formulario(CadastroUsuarioForm, request.data)
        return Response(self.get_serializer(usuario).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def acesso(self, request, pk=None):
        usuario = self.get_object()
        if usuario.e_admin:
            return Response({"detail": "O acesso do administrador fica sempre ativo."}, status=status.HTTP_400_BAD_REQUEST)
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=["is_active"])
        return Response(self.get_serializer(usuario).data)


@method_decorator(csrf_exempt, name="dispatch")
class PermissaoViewSet(viewsets.ViewSet):
    permission_classes = [PermissaoAdmin]

    def list(self, request):
        ligados = set(PermissaoModulo.objects.values_list("perfil", "modulo"))
        linhas = []
        for modulo in Modulo:
            if modulo == Modulo.CADERNO:
                continue
            configuravel = modulo in MODULOS_CONFIGURAVEIS
            linhas.append({
                "modulo": modulo.value,
                "rotulo": modulo.label,
                "configuravel": configuravel,
                "celulas": [
                    {"perfil": perfil.value, "ligado": configuravel and (perfil.value, modulo.value) in ligados}
                    for perfil in PERFIS_CONFIGURAVEIS
                ],
            })
        return Response(linhas)

    def create(self, request):
        perfil = request.data.get("perfil")
        modulo = request.data.get("modulo")
        if perfil not in [p.value for p in PERFIS_CONFIGURAVEIS] or modulo not in MODULOS_CONFIGURAVEIS:
            return Response({"detail": "Perfil ou módulo não pode ser alterado."}, status=status.HTTP_400_BAD_REQUEST)
        liberar = str(request.data.get("liberado")) in ("1", "true", "True")
        if liberar:
            PermissaoModulo.objects.get_or_create(perfil=perfil, modulo=modulo)
        else:
            PermissaoModulo.objects.filter(perfil=perfil, modulo=modulo).delete()
        return Response({"perfil": perfil, "modulo": modulo, "liberado": liberar})
