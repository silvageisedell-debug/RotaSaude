from django.test import TestCase

from contas.models import Perfil
from contas.tests import criar_usuario

from .models import Veiculo
from .tests import criar_modelo, criar_veiculo


class VeiculoApiTests(TestCase):
    def setUp(self):
        self.admin = criar_usuario("admin@rotasaude.com.br", Perfil.ADMIN)
        self.atendente = criar_usuario("atendente@rotasaude.com.br")
        self.client.force_login(self.admin)

    def test_lista_veiculos_em_json(self):
        criar_veiculo()
        resposta = self.client.get("/api/veiculos/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "application/json")
        item = resposta.json()[0]
        self.assertEqual(item["placa"], "ABC-1D23")
        self.assertEqual(item["chassi"], "9BWZZZ377VT004251")
        self.assertIn("modelo_nome", item)

    def test_post_cria_veiculo(self):
        modelo = criar_modelo()
        resposta = self.client.post(
            "/api/veiculos/",
            {
                "tipo": "van",
                "modelo": modelo.pk,
                "placa": "QWE-1A23",
                "chassi": "8AWZZZ377VT009991",
                "ano": 2024,
                "capacidade": 8,
            },
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 201, resposta.content)
        self.assertEqual(resposta.json()["placa"], "QWE-1A23")
        self.assertTrue(Veiculo.objects.filter(placa="QWE1A23", capacidade=8).exists())

    def test_post_recusa_placa_invalida_em_json(self):
        modelo = criar_modelo()
        resposta = self.client.post(
            "/api/veiculos/",
            {
                "tipo": "van",
                "modelo": modelo.pk,
                "placa": "XXX",
                "chassi": "8AWZZZ377VT009991",
                "ano": 2024,
                "capacidade": 8,
            },
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta["Content-Type"], "application/json")
        self.assertIn("placa", resposta.json())
        self.assertFalse(Veiculo.objects.filter(chassi="8AWZZZ377VT009991").exists())

    def test_atendente_nao_lista_nem_cria(self):
        self.client.force_login(self.atendente)
        self.assertEqual(self.client.get("/api/veiculos/").status_code, 403)
        self.assertEqual(self.client.post("/api/veiculos/", {}, content_type="application/json").status_code, 403)

    def test_anonimo_recebe_json(self):
        self.client.logout()
        resposta = self.client.get("/api/veiculos/")
        self.assertEqual(resposta.status_code, 401)
        self.assertEqual(resposta["Content-Type"], "application/json")
