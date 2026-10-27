from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from contas.models import Perfil, Usuario

from .forms import AnotacaoForm
from .models import Anotacao


def criar_usuario(email, perfil=Perfil.ATENDENTE):
    return Usuario.objects.create_user(username=email, email=email, password="senha123", nome=email.split("@")[0].title(), perfil=perfil)


class CadernoTests(TestCase):
    def setUp(self):
        self.rafael = criar_usuario("rafael@rotasaude.com.br")
        self.julia = criar_usuario("julia@rotasaude.com.br")
        self.client.force_login(self.rafael)

    def test_nao_mexe_na_anotacao_de_outro(self):
        alheia = Anotacao.objects.create(usuario=self.julia, texto="Recado da Júlia")
        for nome in ("concluir", "apagar", "adiar"):
            resposta = self.client.post(reverse(f"caderno:{nome}", args=[alheia.pk]))
            self.assertEqual(resposta.status_code, 404, nome)
        self.assertTrue(Anotacao.objects.filter(pk=alheia.pk).exists())

    def test_lembrete_no_passado_e_recusado(self):
        passado = timezone.localtime() - timedelta(hours=1)
        form = AnotacaoForm({"titulo": "", "texto": "Ligar para a UBS", "lembrar_em": passado.strftime("%Y-%m-%dT%H:%M"), "cor": 0, "fixada": False})
        self.assertFalse(form.is_valid())
        self.assertIn("lembrar_em", form.errors)

    def test_anotacao_vazia_e_recusada(self):
        form = AnotacaoForm({"titulo": "", "texto": " ", "cor": 0, "fixada": False})
        self.assertFalse(form.is_valid())

    def test_salvar_pela_view(self):
        resposta = self.client.post(reverse("caderno:inicio"), {"titulo": "Escala", "texto": "Conferir vans", "lembrar_em": "", "cor": "2", "fixada": "True"})
        self.assertRedirects(resposta, reverse("caderno:inicio"), fetch_redirect_response=False)
        nota = Anotacao.objects.get()
        self.assertEqual(nota.usuario, self.rafael)
        self.assertTrue(nota.fixada)
        self.assertEqual(nota.cor, 2)

    def test_editar_anotacao_de_outro_da_404(self):
        alheia = Anotacao.objects.create(usuario=self.julia, texto="Recado")
        resposta = self.client.post(reverse("caderno:inicio"), {"editar": alheia.pk, "texto": "invadido", "cor": "0", "fixada": "False"})
        self.assertEqual(resposta.status_code, 404)

    def test_adiar_define_novo_horario_e_limpa_aviso(self):
        antes = timezone.now() - timedelta(minutes=5)
        nota = Anotacao.objects.create(usuario=self.rafael, texto="Lembrete", lembrar_em=antes, avisado_para=antes)
        self.client.post(reverse("caderno:adiar", args=[nota.pk]), {"minutos": "60"})
        nota.refresh_from_db()
        self.assertIsNone(nota.avisado_para)
        self.assertGreater(nota.lembrar_em, timezone.now() + timedelta(minutes=55))

    def test_adiar_para_amanha_as_8(self):
        nota = Anotacao.objects.create(usuario=self.rafael, texto="Lembrete", lembrar_em=timezone.now())
        self.client.post(reverse("caderno:adiar", args=[nota.pk]), {"minutos": "1440"})
        nota.refresh_from_db()
        local = timezone.localtime(nota.lembrar_em)
        self.assertEqual(local.date(), timezone.localdate() + timedelta(days=1))
        self.assertEqual((local.hour, local.minute), (8, 0))

    def test_avisado_marca_vencidas(self):
        vencida = Anotacao.objects.create(usuario=self.rafael, texto="A", lembrar_em=timezone.now() - timedelta(minutes=1))
        futura = Anotacao.objects.create(usuario=self.rafael, texto="B", lembrar_em=timezone.now() + timedelta(hours=1))
        self.client.post(reverse("caderno:avisado"))
        vencida.refresh_from_db()
        futura.refresh_from_db()
        self.assertEqual(vencida.avisado_para, vencida.lembrar_em)
        self.assertIsNone(futura.avisado_para)
        self.assertIn(vencida, Anotacao.vencidas_de(self.rafael))
        self.assertNotIn(futura, Anotacao.vencidas_de(self.rafael))

    def test_concluir_alterna(self):
        nota = Anotacao.objects.create(usuario=self.rafael, texto="A")
        url = reverse("caderno:concluir", args=[nota.pk])
        self.client.post(url)
        nota.refresh_from_db()
        self.assertTrue(nota.concluida)
        self.client.post(url)
        nota.refresh_from_db()
        self.assertFalse(nota.concluida)

    def test_caderno_bloqueado_para_outros_perfis(self):
        self.client.force_login(criar_usuario("aux@rotasaude.com.br", Perfil.AUXADM))
        self.assertEqual(self.client.get(reverse("caderno:inicio")).status_code, 403)
