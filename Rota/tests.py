from datetime import timedelta

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from Veiculo.models import Marca, Modelo, Veiculo

from .models import CategoriaRota, Disponibilidade
from .seeds import semear_categorias


class NovaDisponibilidadeTests(TestCase):
    def setUp(self):
        marca = Marca.objects.create(nome="Toyota")
        modelo = Modelo.objects.create(nome="Corolla", marca=marca)
        self.veiculo = Veiculo.objects.create(
            placa="ABC1D23",
            modelo=modelo,
            ano=2024,
            chassi="12345678901234567",
            renavam="12345678901",
            capacidade=4,
        )
        self.url = "/disponibilidade/nova/"

    def test_get_mostra_select_de_veiculo(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        html = resposta.content.decode()
        self.assertIn("<select", html)
        self.assertNotIn('type="text"', html)
        self.assertNotIn("name=\"placa\"", html)
        self.assertContains(resposta, "ABC1D23 - Toyota Corolla")

    def test_post_data_passada_nao_grava(self):
        ontem = (timezone.localdate() - timedelta(days=1)).isoformat()
        resposta = self.client.post(self.url, {
            "veiculo": self.veiculo.pk,
            "data": ontem,
            "horario": "08:00",
            "vagas": "3",
        })
        self.assertEqual(Disponibilidade.objects.count(), 0)
        self.assertContains(resposta, "A data não pode ser anterior a hoje.")

    def test_post_sem_horario_nao_grava(self):
        hoje = timezone.localdate().isoformat()
        resposta = self.client.post(self.url, {
            "veiculo": self.veiculo.pk,
            "data": hoje,
            "horario": "",
            "vagas": "3",
        })
        self.assertEqual(Disponibilidade.objects.count(), 0)
        self.assertContains(resposta, "Informe o horário.")

    def test_post_valido_grava_e_mostra_sucesso(self):
        hoje = timezone.localdate()
        resposta = self.client.post(self.url, {
            "veiculo": self.veiculo.pk,
            "data": hoje.isoformat(),
            "horario": "08:30",
            "vagas": "3",
        })
        self.assertEqual(Disponibilidade.objects.count(), 1)
        registro = Disponibilidade.objects.get()
        self.assertEqual(registro.veiculo, self.veiculo)
        self.assertEqual(registro.data, hoje)
        self.assertEqual(registro.vagas, 3)
        self.assertContains(resposta, "Disponibilidade registrada")
        self.assertContains(resposta, "ABC1D23 - Toyota Corolla")
        self.assertContains(resposta, hoje.strftime("%d/%m/%Y"))
        self.assertContains(resposta, "08:30")
        self.assertContains(resposta, "3 vagas")


class CategoriaRotaTests(TestCase):
    def test_nome_duplicado_nao_grava(self):
        self.assertEqual(CategoriaRota.objects.filter(nome="Urgente").count(), 1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CategoriaRota.objects.create(nome="Urgente", prioridade=9)
        self.assertEqual(CategoriaRota.objects.filter(nome="Urgente").count(), 1)
        self.assertEqual(CategoriaRota.objects.get(nome="Urgente").prioridade, 1)

    def test_seed_cria_as_tres_categorias(self):
        por_nome = dict(CategoriaRota.objects.values_list("nome", "prioridade"))
        self.assertEqual(por_nome["Urgente"], 1)
        self.assertEqual(por_nome["Prioritária"], 2)
        self.assertEqual(por_nome["Eletiva"], 3)

    def test_seed_repetido_nao_duplica(self):
        antes = CategoriaRota.objects.count()
        semear_categorias(apps, None)
        semear_categorias(apps, None)
        self.assertEqual(CategoriaRota.objects.count(), antes)
        self.assertEqual(CategoriaRota.objects.filter(nome="Urgente").count(), 1)
        self.assertEqual(CategoriaRota.objects.filter(nome="Prioritária").count(), 1)
        self.assertEqual(CategoriaRota.objects.filter(nome="Eletiva").count(), 1)

    def test_ordenacao_segue_prioridade_depois_nome(self):
        nomes = list(CategoriaRota.objects.values_list("nome", flat=True))
        self.assertEqual(nomes, ["Urgente", "Prioritária", "Eletiva"])

    def test_mesma_prioridade_em_nomes_diferentes_e_aceita(self):
        CategoriaRota.objects.create(nome="Retorno", prioridade=1)
        self.assertEqual(CategoriaRota.objects.filter(prioridade=1).count(), 2)

    def test_admin_lista_nome_e_prioridade(self):
        usuario = get_user_model().objects.create_superuser(
            username="igor",
            email="igor@example.com",
            password="senha-admin-123",
        )
        self.client.force_login(usuario)
        resposta = self.client.get(reverse("admin:Rota_categoriarota_changelist"))
        self.assertEqual(resposta.status_code, 200)
        html = resposta.content.decode()
        self.assertLess(html.index("Urgente"), html.index("Prioritária"))
        self.assertLess(html.index("Prioritária"), html.index("Eletiva"))
        self.assertContains(resposta, "Prioridade")
