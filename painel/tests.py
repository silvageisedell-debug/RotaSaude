from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from contas.models import Perfil, PermissaoModulo, Usuario
from frota.models import Motorista, Veiculo
from solicitacoes.models import Solicitacao
from viagens.models import Viagem


class NavegacaoTests(TestCase):
    def test_raiz_leva_anonimo_ao_login(self):
        resposta = self.client.get("/")
        self.assertRedirects(resposta, reverse("contas:login"), fetch_redirect_response=False)

    def test_raiz_leva_logado_ao_inicio(self):
        usuario = Usuario.objects.create_user(username="a@x.com", email="a@x.com", password="senha123", nome="A", perfil=Perfil.ATENDENTE)
        self.client.force_login(usuario)
        resposta = self.client.get("/")
        self.assertRedirects(resposta, reverse("painel:inicio"), fetch_redirect_response=False)

    def test_sem_inicio_vai_para_primeiro_modulo(self):
        PermissaoModulo.objects.filter(perfil="auxadm", modulo="inicio").delete()
        usuario = Usuario.objects.create_user(username="b@x.com", email="b@x.com", password="senha123", nome="B", perfil=Perfil.AUXADM)
        self.client.force_login(usuario)
        resposta = self.client.get(reverse("painel:inicio"))
        self.assertRedirects(resposta, reverse("solicitacoes:lista"), fetch_redirect_response=False)

    def test_sem_nenhum_modulo_vai_para_aviso(self):
        PermissaoModulo.objects.filter(perfil="administrativo").delete()
        usuario = Usuario.objects.create_user(username="c@x.com", email="c@x.com", password="senha123", nome="C", perfil=Perfil.ADMINISTRATIVO)
        self.client.force_login(usuario)
        resposta = self.client.get("/")
        self.assertRedirects(resposta, reverse("painel:sem_modulo"), fetch_redirect_response=False)


class PopularDemoTests(TestCase):
    def test_roda_duas_vezes_sem_duplicar(self):
        call_command("popular_demo", stdout=StringIO())
        contagem = (Usuario.objects.count(), Veiculo.objects.count(), Motorista.objects.count(),
                    Solicitacao.objects.count(), Viagem.objects.count())
        call_command("popular_demo", stdout=StringIO())
        self.assertEqual(
            contagem,
            (Usuario.objects.count(), Veiculo.objects.count(), Motorista.objects.count(),
             Solicitacao.objects.count(), Viagem.objects.count()),
        )
        self.assertEqual(contagem, (2, 7, 6, 6, 2))
        self.assertEqual(Viagem.objects.filter(status=Viagem.Status.EM_ANDAMENTO).count(), 1)
        self.assertTrue(Usuario.objects.get(email="admin@rotasaude.com.br").check_password("admin123"))
