from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from Veiculo.models import Marca, Modelo, Veiculo

from .models import Disponibilidade


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
