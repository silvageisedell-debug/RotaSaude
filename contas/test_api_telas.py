from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token

from contas.models import Perfil
from contas.tests import criar_usuario
from frota.tests import criar_modelo, criar_veiculo


class ApiTelasTests(TestCase):
    def setUp(self):
        self.admin = criar_usuario("admin@rotasaude.com.br", Perfil.ADMIN, nome="Carla Administradora", senha="admin123")
        self.atendente = criar_usuario("atendente@rotasaude.com.br", nome="Rafael Atendente", senha="atend123")

    def token(self, usuario):
        chave = Token.objects.create(user=usuario).key
        return {"HTTP_AUTHORIZATION": f"Token {chave}"}

    def test_login_devolve_token_em_json(self):
        resposta = self.client.post(
            "/api/entrar/",
            {"email": "admin@rotasaude.com.br", "senha": "admin123"},
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 200, resposta.content)
        corpo = resposta.json()
        self.assertIn("token", corpo)
        self.assertEqual(corpo["usuario"]["email"], "admin@rotasaude.com.br")
        self.assertEqual(resposta["Content-Type"], "application/json")

    def test_listas_do_admin_em_json(self):
        criar_veiculo()
        cabecalho = self.token(self.admin)
        for url in (
            "/api/veiculos/", "/api/modelos/", "/api/motoristas/", "/api/pontos/",
            "/api/pedidos-ponto/", "/api/usuarios/", "/api/permissoes/",
            "/api/categorias/", "/api/destinos/", "/api/solicitacoes/",
            "/api/viagens/", "/api/inicio/", "/api/resumo/",
        ):
            resposta = self.client.get(url, **cabecalho)
            self.assertEqual(resposta.status_code, 200, url)
            self.assertEqual(resposta["Content-Type"], "application/json", url)
            self.assertNotIn("<html", resposta.content.decode().lower())

    def test_atendente_ve_caderno_e_nao_ve_frota(self):
        cabecalho = self.token(self.atendente)
        self.assertEqual(self.client.get("/api/anotacoes/", **cabecalho).status_code, 200)
        self.assertEqual(self.client.get("/api/veiculos/", **cabecalho).status_code, 403)
        self.assertEqual(self.client.get("/api/usuarios/", **cabecalho).status_code, 403)

    def test_post_veiculo_com_token_sem_csrf(self):
        modelo = criar_modelo()
        resposta = self.client.post(
            "/api/veiculos/",
            {
                "tipo": "van", "modelo": modelo.pk, "placa": "QWE-1A23",
                "chassi": "8AWZZZ377VT009991", "ano": 2024, "capacidade": 8,
            },
            content_type="application/json",
            **self.token(self.admin),
        )
        self.assertEqual(resposta.status_code, 201, resposta.content)
        self.assertEqual(resposta.json()["placa"], "QWE-1A23")

    def test_post_anotacao_do_atendente(self):
        resposta = self.client.post(
            "/api/anotacoes/",
            {"titulo": "Lembrete", "texto": "Ligar para o paciente", "cor": 0, "fixada": False},
            content_type="application/json",
            **self.token(self.atendente),
        )
        self.assertEqual(resposta.status_code, 201, resposta.content)
        self.assertEqual(resposta.json()["titulo"], "Lembrete")

    def test_login_com_senha_errada_e_json(self):
        resposta = self.client.post(
            "/api/entrar/",
            {"email": "admin@rotasaude.com.br", "senha": "errada"},
            content_type="application/json",
        )
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(resposta["Content-Type"], "application/json")
        self.assertNotIn("<html", resposta.content.decode().lower())

    def test_validade_de_cnh_no_futuro_entra_no_cadastro(self):
        validade = (timezone.localdate() + timedelta(days=400)).isoformat()
        resposta = self.client.post(
            "/api/motoristas/",
            {
                "nome": "Ana Paula Ferreira", "cpf": "23456789254", "cnh": "01234502222",
                "categoria_cnh": "D", "validade_cnh": validade, "telefone": "", "curso_emergencia": True,
            },
            content_type="application/json",
            **self.token(self.admin),
        )
        self.assertEqual(resposta.status_code, 201, resposta.content)
        self.assertIn("***", resposta.json()["cpf"])
