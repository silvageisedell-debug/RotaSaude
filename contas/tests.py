from django.contrib.auth import authenticate
from django.test import TestCase
from django.urls import reverse

from .forms import MSG_INATIVO, CadastroUsuarioForm, LoginForm, SolicitarAcessoForm
from .models import Modulo, Perfil, PermissaoModulo, Usuario


def criar_usuario(email, perfil=Perfil.ATENDENTE, nome=None, ativo=True, senha="senha123"):
    usuario = Usuario.objects.create_user(
        username=email, email=email, password=senha, nome=nome or email.split("@")[0].title(), perfil=perfil
    )
    if not ativo:
        usuario.is_active = False
        usuario.save()
    return usuario


class LoginTests(TestCase):
    def setUp(self):
        self.usuario = criar_usuario("rafael@rotasaude.com.br", nome="Rafael Atendente")

    def test_backend_aceita_email_sem_diferenciar_maiusculas(self):
        self.assertEqual(authenticate(email="RAFAEL@RotaSaude.com.br", password="senha123"), self.usuario)

    def test_senha_errada_nao_autentica(self):
        self.assertIsNone(authenticate(email="rafael@rotasaude.com.br", password="errada"))

    def test_usuario_inativo_recebe_mensagem_de_acesso_pendente(self):
        criar_usuario("novo@rotasaude.com.br", ativo=False)
        form = LoginForm({"email": "novo@rotasaude.com.br", "senha": "senha123"})
        self.assertFalse(form.is_valid())
        self.assertIn(MSG_INATIVO, form.non_field_errors())

    def test_post_valido_redireciona_para_primeiro_modulo(self):
        resposta = self.client.post(reverse("contas:login"), {"email": "rafael@rotasaude.com.br", "senha": "senha123"})
        self.assertRedirects(resposta, reverse("painel:inicio"), fetch_redirect_response=False)

    def test_sair_exige_post(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("contas:sair")).status_code, 405)
        resposta = self.client.post(reverse("contas:sair"))
        self.assertRedirects(resposta, reverse("contas:login"), fetch_redirect_response=False)


class CadastroTests(TestCase):
    def test_solicitar_acesso_cria_atendente_inativo(self):
        form = SolicitarAcessoForm({
            "nome": "Joana Silva", "email": "Joana@Email.com", "senha": "segredo1",
            "confirmar": "segredo1", "lgpd": "on",
        })
        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()
        self.assertFalse(usuario.is_active)
        self.assertEqual(usuario.perfil, Perfil.ATENDENTE)
        self.assertEqual(usuario.email, "joana@email.com")

    def test_solicitar_acesso_sem_lgpd_e_senhas_diferentes_nao_grava(self):
        form = SolicitarAcessoForm({
            "nome": "Joana Silva", "email": "joana@email.com", "senha": "segredo1", "confirmar": "outra123",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("lgpd", form.errors)
        self.assertIn("As senhas não conferem.", form.errors["confirmar"])

    def test_email_repetido_e_recusado(self):
        criar_usuario("joana@email.com")
        form = CadastroUsuarioForm({"nome": "Outra Pessoa", "email": "JOANA@email.com", "senha": "segredo1", "perfil": "auxadm"})
        self.assertFalse(form.is_valid())
        self.assertIn("Este e-mail já está cadastrado.", form.errors["email"])

    def test_admin_cadastra_usuario_ja_liberado(self):
        admin = criar_usuario("admin@rotasaude.com.br", perfil=Perfil.ADMIN)
        self.client.force_login(admin)
        resposta = self.client.post(reverse("contas:usuarios"), {
            "nome": "Bruno Auxiliar", "email": "bruno@rotasaude.com.br", "senha": "segredo1", "perfil": "auxadm",
        })
        self.assertRedirects(resposta, reverse("contas:usuarios"), fetch_redirect_response=False)
        bruno = Usuario.objects.get(email="bruno@rotasaude.com.br")
        self.assertTrue(bruno.is_active)
        self.assertEqual(bruno.perfil, Perfil.AUXADM)
        self.assertTrue(bruno.check_password("segredo1"))


class AcessoTests(TestCase):
    def setUp(self):
        self.admin = criar_usuario("admin@rotasaude.com.br", perfil=Perfil.ADMIN)
        self.atendente = criar_usuario("atendente@rotasaude.com.br")

    def test_alternar_acesso_liga_e_desliga(self):
        self.client.force_login(self.admin)
        url = reverse("contas:alternar_acesso", args=[self.atendente.pk])
        self.client.post(url)
        self.atendente.refresh_from_db()
        self.assertFalse(self.atendente.is_active)
        self.client.post(url)
        self.atendente.refresh_from_db()
        self.assertTrue(self.atendente.is_active)

    def test_acesso_do_admin_nao_e_desligado(self):
        outro = criar_usuario("chefe@rotasaude.com.br", perfil=Perfil.ADMIN)
        self.client.force_login(self.admin)
        self.client.post(reverse("contas:alternar_acesso", args=[outro.pk]))
        outro.refresh_from_db()
        self.assertTrue(outro.is_active)

    def test_nao_admin_recebe_403_em_usuarios_e_permissoes(self):
        self.client.force_login(self.atendente)
        self.assertEqual(self.client.get(reverse("contas:usuarios")).status_code, 403)
        self.assertEqual(self.client.get(reverse("contas:permissoes")).status_code, 403)
        self.assertEqual(self.client.post(reverse("contas:alternar_acesso", args=[self.admin.pk])).status_code, 403)

    def test_anonimo_vai_para_login(self):
        resposta = self.client.get(reverse("contas:usuarios"))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("contas:login"), resposta["Location"])


class PermissoesTests(TestCase):
    def setUp(self):
        self.admin = criar_usuario("admin@rotasaude.com.br", perfil=Perfil.ADMIN)
        self.aux = criar_usuario("aux@rotasaude.com.br", perfil=Perfil.AUXADM)

    def test_seed_libera_inicio_solicitacoes_e_viagens(self):
        for perfil in ("atendente", "auxadm", "administrativo"):
            modulos = set(PermissaoModulo.objects.filter(perfil=perfil).values_list("modulo", flat=True))
            self.assertEqual(modulos, {"inicio", "solicitacoes", "viagens"})

    def test_matriz_liga_e_desliga_modulo(self):
        self.client.force_login(self.admin)
        self.assertFalse(self.aux.pode(Modulo.FROTA))
        self.client.post(reverse("contas:permissoes"), {"perfil": "auxadm", "modulo": "frota", "liberado": "1"})
        self.assertTrue(self.aux.pode(Modulo.FROTA))
        self.assertIn("frota", self.aux.modulos())
        self.client.post(reverse("contas:permissoes"), {"perfil": "auxadm", "modulo": "frota", "liberado": "0"})
        self.assertFalse(self.aux.pode(Modulo.FROTA))
        self.assertNotIn("frota", self.aux.modulos())

    def test_matriz_ignora_modulos_so_do_admin(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("contas:permissoes"), {"perfil": "auxadm", "modulo": "usuarios", "liberado": "1"})
        self.assertFalse(PermissaoModulo.objects.filter(modulo="usuarios").exists())
        self.assertFalse(self.aux.pode(Modulo.USUARIOS))

    def test_caderno_so_para_atendente(self):
        atendente = criar_usuario("at@rotasaude.com.br")
        self.assertTrue(atendente.pode(Modulo.CADERNO))
        self.assertIn("caderno", atendente.modulos())
        self.assertFalse(self.aux.pode(Modulo.CADERNO))
        self.assertFalse(self.admin.pode(Modulo.CADERNO))

    def test_admin_ve_todos_os_modulos_de_gestao(self):
        self.assertEqual(
            list(self.admin.modulos()),
            ["inicio", "solicitacoes", "viagens", "frota", "usuarios", "permissoes"],
        )

    def test_superuser_vira_admin(self):
        su = Usuario.objects.create_superuser(username="su@x.com", email="su@x.com", password="segredo1")
        self.assertEqual(su.perfil, Perfil.ADMIN)
