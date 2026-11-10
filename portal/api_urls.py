from django.urls import path
from rest_framework.routers import DefaultRouter

from caderno.viewsets import AnotacaoViewSet
from contas.viewsets import EntrarView, PermissaoViewSet, SairView, UsuarioViewSet
from frota.viewsets import ModeloViewSet, MotoristaViewSet, PedidoPontoViewSet, PontoEmbarqueViewSet, VeiculoViewSet
from painel.viewsets import InicioViewSet, ResumoViewSet
from solicitacoes.viewsets import CategoriaViewSet, DestinoViewSet, SolicitacaoViewSet
from viagens.viewsets import ViagemViewSet

router = DefaultRouter()
router.register("veiculos", VeiculoViewSet, basename="veiculo")
router.register("modelos", ModeloViewSet, basename="modelo")
router.register("motoristas", MotoristaViewSet, basename="motorista")
router.register("pontos", PontoEmbarqueViewSet, basename="ponto")
router.register("pedidos-ponto", PedidoPontoViewSet, basename="pedido-ponto")
router.register("usuarios", UsuarioViewSet, basename="usuario")
router.register("permissoes", PermissaoViewSet, basename="permissao")
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("destinos", DestinoViewSet, basename="destino")
router.register("solicitacoes", SolicitacaoViewSet, basename="solicitacao")
router.register("viagens", ViagemViewSet, basename="viagem")
router.register("anotacoes", AnotacaoViewSet, basename="anotacao")
router.register("inicio", InicioViewSet, basename="inicio")
router.register("resumo", ResumoViewSet, basename="resumo")

urlpatterns = [
    path("entrar/", EntrarView.as_view(), name="api-entrar"),
    path("sair/", SairView.as_view(), name="api-sair"),
    *router.urls,
]
