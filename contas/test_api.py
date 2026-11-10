from django.test import TestCase

from .models import Perfil
from .tests import criar_usuario


class UsuarioApiTests(TestCase):
    def setUp(self):
        self.admin = criar_usuario("admin@rotasaude.com.br", Perfil.ADMIN, nome="Carla Administradora")
        self.atendente = criar_usuario("atendente@rotasaude.com.br", nome="Rafael Atendente")

    def test_admin_lista_usuarios_em_json(self):
        self.client.force_login(self.admin)
        resposta = self.client.get("/api/usuarios/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "application/json")
        emails = [item["email"] for item in resposta.json()]
        self.assertIn(self.admin.email, emails)
        self.assertIn(self.atendente.email, emails)
        self.assertNotIn("password", resposta.json()[0])

    def test_atendente_nao_lista_usuarios(self):
        self.client.force_login(self.atendente)
        resposta = self.client.get("/api/usuarios/")
        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(resposta["Content-Type"], "application/json")

    def test_anonimo_nao_lista_usuarios(self):
        resposta = self.client.get("/api/usuarios/")
        self.assertEqual(resposta.status_code, 401)
        self.assertEqual(resposta["Content-Type"], "application/json")
