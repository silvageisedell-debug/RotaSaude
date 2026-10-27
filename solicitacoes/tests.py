from datetime import time, timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from contas.models import Perfil, Usuario
from frota.models import PontoEmbarque

from . import services
from .forms import SolicitacaoForm
from .models import Categoria, Destino, Solicitacao


def criar_usuario(email="atendente@rotasaude.com.br", perfil=Perfil.ATENDENTE):
    return Usuario.objects.create_user(username=email, email=email, password="senha123", nome="Rafael Atendente", perfil=perfil)


def criar_solicitacao(usuario, paciente="Maria das Dores", status=Solicitacao.Status.PENDENTE, dias=1, acompanhante=False, **extras):
    dados = {
        "paciente": paciente,
        "categoria": Categoria.objects.get(nome="Eletiva"),
        "ponto_embarque": PontoEmbarque.objects.get(nome="UBS Centro"),
        "destino": Destino.objects.get(cidade="Barretos"),
        "data": timezone.localdate() + timedelta(days=dias),
        "horario": time(7, 0),
        "acompanhante": acompanhante,
        "status": status,
        "criado_por": usuario,
    }
    dados.update(extras)
    return Solicitacao.objects.create(**dados)


class SeedTests(TestCase):
    def test_categorias_na_ordem_de_prioridade(self):
        self.assertEqual(list(Categoria.objects.values_list("nome", flat=True)), ["Urgente", "Prioritária", "Eletiva"])
        self.assertEqual(Categoria.objects.get(nome="Urgente").prioridade, 1)

    def test_nome_de_categoria_unico(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Categoria.objects.create(nome="Urgente", prioridade=9)

    def test_destinos_semeados(self):
        cidades = set(Destino.objects.values_list("cidade", flat=True))
        self.assertEqual(cidades, {"Barretos", "São José do Rio Preto", "Ribeirão Preto"})


class FormTests(TestCase):
    def _dados(self, **extras):
        dados = {
            "paciente": "  José   Almeida ", "telefone": "", "tipo": "consulta",
            "categoria": Categoria.objects.get(nome="Urgente").pk,
            "ponto_embarque": PontoEmbarque.objects.get(nome="UBS Centro").pk,
            "destino": Destino.objects.get(cidade="Barretos").pk,
            "data": (timezone.localdate() + timedelta(days=1)).isoformat(), "horario": "07:00",
            "mobilidade": "anda", "observacoes": "",
        }
        dados.update(extras)
        return dados

    def test_valido_normaliza_nome(self):
        form = SolicitacaoForm(self._dados())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["paciente"], "José Almeida")

    def test_data_passada_nao_grava(self):
        ontem = (timezone.localdate() - timedelta(days=1)).isoformat()
        form = SolicitacaoForm(self._dados(data=ontem))
        self.assertFalse(form.is_valid())
        self.assertIn("Escolha uma data a partir de hoje.", form.errors["data"])

    def test_ponto_removido_nao_aparece(self):
        ponto = PontoEmbarque.objects.get(nome="UBS Centro")
        ponto.ativo = False
        ponto.save()
        form = SolicitacaoForm(self._dados(ponto_embarque=ponto.pk))
        self.assertFalse(form.is_valid())
        self.assertIn("ponto_embarque", form.errors)

    def test_view_nova_registra_e_cria_historico(self):
        usuario = criar_usuario()
        self.client.force_login(usuario)
        resposta = self.client.post(reverse("solicitacoes:nova"), self._dados())
        solicitacao = Solicitacao.objects.get()
        self.assertRedirects(resposta, reverse("solicitacoes:detalhe", args=[solicitacao.pk]), fetch_redirect_response=False)
        self.assertEqual(solicitacao.status, Solicitacao.Status.PENDENTE)
        self.assertEqual(solicitacao.criado_por, usuario)
        self.assertEqual(solicitacao.historico.count(), 1)
        self.assertIn("Registrada pelo atendimento", solicitacao.historico.get().texto)


class TransicoesTests(TestCase):
    def setUp(self):
        self.usuario = criar_usuario()

    def test_aprovar_pendente(self):
        s = criar_solicitacao(self.usuario)
        services.aprovar(s, self.usuario)
        s.refresh_from_db()
        self.assertEqual(s.status, Solicitacao.Status.APROVADA)
        self.assertEqual(s.historico.count(), 1)

    def test_aprovar_duas_vezes_falha(self):
        s = criar_solicitacao(self.usuario, status=Solicitacao.Status.APROVADA)
        with self.assertRaises(ValueError):
            services.aprovar(s, self.usuario)

    def test_recusar_guarda_motivo(self):
        s = criar_solicitacao(self.usuario)
        services.recusar(s, "Sem vaga nessa data", self.usuario)
        s.refresh_from_db()
        self.assertEqual(s.status, Solicitacao.Status.NEGADA)
        self.assertEqual(s.motivo_recusa, "Sem vaga nessa data")
        self.assertIn("Sem vaga nessa data", s.historico.last().texto)

    def test_recusar_agendada_falha(self):
        s = criar_solicitacao(self.usuario, status=Solicitacao.Status.AGENDADA)
        with self.assertRaises(ValueError):
            services.recusar(s, "Motivo qualquer", self.usuario)

    def test_cancelar_pendente_e_nao_concluida(self):
        s = criar_solicitacao(self.usuario)
        services.cancelar(s, self.usuario)
        s.refresh_from_db()
        self.assertEqual(s.status, Solicitacao.Status.CANCELADA)
        concluida = criar_solicitacao(self.usuario, status=Solicitacao.Status.CONCLUIDA)
        with self.assertRaises(ValueError):
            services.cancelar(concluida, self.usuario)

    def test_view_aprovar_exige_post(self):
        s = criar_solicitacao(self.usuario)
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("solicitacoes:aprovar", args=[s.pk])).status_code, 405)
        resposta = self.client.post(reverse("solicitacoes:aprovar", args=[s.pk]))
        self.assertRedirects(resposta, reverse("solicitacoes:lista"), fetch_redirect_response=False)
        s.refresh_from_db()
        self.assertEqual(s.status, Solicitacao.Status.APROVADA)

    def test_view_aprovar_ignora_voltar_externo(self):
        s = criar_solicitacao(self.usuario)
        self.client.force_login(self.usuario)
        resposta = self.client.post(reverse("solicitacoes:aprovar", args=[s.pk]), {"voltar": "https://exemplo.com/"})
        self.assertEqual(resposta["Location"], reverse("solicitacoes:lista"))

    def test_view_recusar_com_motivo(self):
        s = criar_solicitacao(self.usuario)
        self.client.force_login(self.usuario)
        self.client.post(reverse("solicitacoes:recusar", args=[s.pk]), {"motivo": "Paciente sem laudo"})
        s.refresh_from_db()
        self.assertEqual(s.status, Solicitacao.Status.NEGADA)

    def test_lugares_conta_acompanhante(self):
        self.assertEqual(criar_solicitacao(self.usuario, acompanhante=True).lugares, 2)
        self.assertEqual(criar_solicitacao(self.usuario, paciente="Outro").lugares, 1)


class ListaTests(TestCase):
    def setUp(self):
        self.usuario = criar_usuario()
        self.client.force_login(self.usuario)
        self.maria = criar_solicitacao(self.usuario, paciente="Maria das Dores")
        self.jose = criar_solicitacao(self.usuario, paciente="José Almeida", status=Solicitacao.Status.APROVADA)
        criar_solicitacao(self.usuario, paciente="Cancelado Silva", status=Solicitacao.Status.CANCELADA)

    def test_kanban_agrupa_por_status(self):
        resposta = self.client.get(reverse("solicitacoes:lista"))
        colunas = dict(resposta.context["colunas"])
        self.assertEqual(colunas["Pendente"], [self.maria])
        self.assertEqual(colunas["Aprovada"], [self.jose])
        self.assertNotIn("Cancelada", colunas)

    def test_lista_filtra_por_status(self):
        resposta = self.client.get(reverse("solicitacoes:lista"), {"modo": "lista", "status": "aprovada"})
        self.assertEqual(list(resposta.context["solicitacoes"]), [self.jose])

    def test_busca_por_codigo_e_nome(self):
        codigo = self.maria.codigo
        resposta = self.client.get(reverse("solicitacoes:lista"), {"modo": "lista", "q": codigo.lower()})
        self.assertIn(self.maria, resposta.context["solicitacoes"])
        resposta = self.client.get(reverse("solicitacoes:lista"), {"modo": "lista", "q": "josé"})
        self.assertEqual(list(resposta.context["solicitacoes"]), [self.jose])

    def test_codigo_formatado(self):
        self.assertEqual(Solicitacao(pk=1).codigo, "SOL-001")
