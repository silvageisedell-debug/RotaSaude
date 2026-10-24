from datetime import timedelta

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from Veiculo.models import Marca, Modelo, Veiculo

from .itinerario import calcular_itinerario
from .models import CategoriaRota, Disponibilidade, Parada, Viagem
from .seeds import semear_categorias


def entrar(client, username="atendente@rotasaude.com.br"):
    usuario = get_user_model().objects.get(username=username)
    client.force_login(usuario)
    return usuario


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
        entrar(self.client)

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


class PublicarRotaTests(TestCase):
    def setUp(self):
        marca = Marca.objects.create(nome="Fiat")
        modelo = Modelo.objects.create(nome="Ducato", marca=marca)
        veiculo = Veiculo.objects.create(
            placa="RTE1A23",
            modelo=modelo,
            ano=2023,
            chassi="76543210987654321",
            renavam="10987654321",
            capacidade=8,
        )
        self.disponibilidade = Disponibilidade.objects.create(
            veiculo=veiculo,
            data=timezone.localdate(),
            horario="09:00",
            vagas=4,
        )
        self.categoria = CategoriaRota.objects.get(nome="Urgente")
        self.url = "/rotas/nova/"
        entrar(self.client)

    def _post(self, **extras):
        dados = {
            "disponibilidade": self.disponibilidade.pk,
            "categoria": self.categoria.pk,
            "origem": "UBS Centro",
            "destino": "Hospital Municipal",
        }
        dados.update(extras)
        return self.client.post(self.url, dados)

    def test_post_sem_origem_nao_grava(self):
        resposta = self._post(origem="")
        self.assertEqual(Viagem.objects.count(), 0)
        self.assertContains(resposta, "Informe a origem.")

    def test_post_sem_destino_nao_grava(self):
        resposta = self._post(destino="")
        self.assertEqual(Viagem.objects.count(), 0)
        self.assertContains(resposta, "Informe o destino.")

    def test_post_sem_disponibilidade_nao_grava(self):
        resposta = self._post(disponibilidade="")
        self.assertEqual(Viagem.objects.count(), 0)
        self.assertContains(resposta, "Selecione uma disponibilidade.")

    def test_post_sem_categoria_nao_grava(self):
        resposta = self._post(categoria="")
        self.assertEqual(Viagem.objects.count(), 0)
        self.assertContains(resposta, "Selecione uma categoria.")

    def test_post_valido_grava_vinculos(self):
        resposta = self._post()
        self.assertEqual(Viagem.objects.count(), 1)
        viagem = Viagem.objects.get()
        self.assertEqual(viagem.disponibilidade, self.disponibilidade)
        self.assertEqual(viagem.categoria, self.categoria)
        self.assertEqual(viagem.origem, "UBS Centro")
        self.assertEqual(viagem.destino, "Hospital Municipal")
        self.assertContains(resposta, "Rota publicada")
        self.assertNotContains(resposta, 'name="placa"')
        self.assertNotContains(resposta, 'name="categoria_nome"')

    def test_lista_mostra_origem_e_destino(self):
        self._post()
        resposta = self.client.get("/rotas/")
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "UBS Centro")
        self.assertContains(resposta, "Hospital Municipal")
        self.assertContains(resposta, "RTE1A23")
        self.assertContains(resposta, "Urgente")

    def test_protect_impede_apagar_disponibilidade_e_categoria_em_uso(self):
        self._post()
        viagem = Viagem.objects.get()
        with self.assertRaises(ProtectedError):
            viagem.disponibilidade.delete()
        with self.assertRaises(ProtectedError):
            viagem.categoria.delete()
        self.assertEqual(Viagem.objects.count(), 1)


class ItinerarioTests(TestCase):
    def setUp(self):
        marca = Marca.objects.create(nome="Renault")
        modelo = Modelo.objects.create(nome="Master", marca=marca)
        veiculo = Veiculo.objects.create(
            placa="ITI9B87",
            modelo=modelo,
            ano=2022,
            chassi="11111111111111111",
            renavam="22222222222",
            capacidade=12,
        )
        self.disponibilidade = Disponibilidade.objects.create(
            veiculo=veiculo,
            data=timezone.localdate(),
            horario="07:15",
            vagas=6,
        )
        self.categoria = CategoriaRota.objects.get(nome="Eletiva")
        entrar(self.client)

    def _dados(self, paradas, **extras):
        dados = {
            "disponibilidade": self.disponibilidade.pk,
            "categoria": self.categoria.pk,
            "origem": "UBS Centro",
            "destino": "Hospital Municipal",
            "paradas-TOTAL_FORMS": str(len(paradas)),
            "paradas-INITIAL_FORMS": "0",
            "paradas-MIN_NUM_FORMS": "0",
            "paradas-MAX_NUM_FORMS": "1000",
        }
        for indice, (local, ordem) in enumerate(paradas):
            dados[f"paradas-{indice}-local"] = local
            dados[f"paradas-{indice}-ordem"] = ordem
        dados.update(extras)
        return dados

    def test_duas_paradas_gravam_na_ordem_numerica(self):
        resposta = self.client.post(
            "/rotas/nova/",
            self._dados([("Hospital Municipal", 2), ("UBS Centro", 1)]),
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Viagem.objects.count(), 1)
        viagem = Viagem.objects.get()
        self.assertEqual(
            list(viagem.paradas.values_list("ordem", "local")),
            [(1, "UBS Centro"), (2, "Hospital Municipal")],
        )
        lista = self.client.get("/rotas/")
        html = lista.content.decode()
        self.assertLess(html.index("1. UBS Centro"), html.index("2. Hospital Municipal"))
        self.assertContains(lista, "8 km")
        self.assertContains(lista, "16 min")

    def test_ordem_repetida_na_mesma_viagem_nao_grava(self):
        resposta = self.client.post(
            "/rotas/nova/",
            self._dados([("UBS Centro", 1), ("Hospital Municipal", 1)]),
        )
        self.assertEqual(Viagem.objects.count(), 0)
        self.assertEqual(Parada.objects.count(), 0)
        self.assertContains(resposta, "A ordem da parada não pode se repetir na mesma rota.")

    def test_mesma_ordem_em_viagens_diferentes_e_aceita(self):
        self.client.post("/rotas/nova/", self._dados([("UBS Centro", 1)]))
        self.client.post(
            "/rotas/nova/",
            self._dados(
                [("Hospital Municipal", 1)],
                origem="Clínica Norte",
                destino="Laboratório",
            ),
        )
        self.assertEqual(Viagem.objects.count(), 2)
        self.assertEqual(Parada.objects.filter(ordem=1).count(), 2)

    def test_editar_inclui_parada(self):
        self.client.post(
            "/rotas/nova/",
            self._dados([("UBS Centro", 1), ("Hospital Municipal", 2)]),
        )
        viagem = Viagem.objects.get()
        resposta = self.client.post(
            f"/rotas/{viagem.pk}/editar/",
            self._dados(
                [
                    ("UBS Centro", 1),
                    ("Hospital Municipal", 2),
                    ("Farmácia Popular", 3),
                ]
            ),
        )
        self.assertContains(resposta, "Rota atualizada")
        self.assertEqual(
            list(viagem.paradas.values_list("ordem", "local")),
            [
                (1, "UBS Centro"),
                (2, "Hospital Municipal"),
                (3, "Farmácia Popular"),
            ],
        )

    def test_editar_com_ordem_repetida_nao_altera(self):
        self.client.post("/rotas/nova/", self._dados([("UBS Centro", 1)]))
        viagem = Viagem.objects.get()
        resposta = self.client.post(
            f"/rotas/{viagem.pk}/editar/",
            self._dados([("UBS Centro", 1), ("Hospital Municipal", 1)]),
        )
        self.assertContains(resposta, "A ordem da parada não pode se repetir na mesma rota.")
        self.assertEqual(list(viagem.paradas.values_list("ordem", "local")), [(1, "UBS Centro")])


class CalculoItinerarioTests(TestCase):
    def test_lista_vazia(self):
        resultado = calcular_itinerario([])
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["sequencia"], [])
        self.assertEqual(resultado["distancia_total_km"], 0)
        self.assertEqual(resultado["tempo_estimado_min"], 0)
        self.assertIn("Lista de paradas vazia.", resultado["avisos"])

    def test_veiculo_sem_capacidade(self):
        resultado = calcular_itinerario([{"local": "UBS", "ordem": 1}], capacidade=0)
        self.assertFalse(resultado["ok"])
        self.assertEqual(resultado["sequencia"], [])
        self.assertIn("Veículo sem capacidade.", resultado["avisos"])

    def test_vagas_acima_da_capacidade(self):
        resultado = calcular_itinerario(
            [{"local": "UBS", "ordem": 1}],
            capacidade=2,
            vagas=4,
        )
        self.assertFalse(resultado["ok"])
        self.assertIn("As vagas passam da capacidade do veículo.", resultado["avisos"])

    def test_duplicado_e_ponto_sem_local(self):
        resultado = calcular_itinerario([
            {"local": "UBS", "ordem": 2},
            {"local": "ubs", "ordem": 1},
            {"local": "  ", "ordem": 3},
            {"local": "Hospital", "ordem": 4},
        ])
        self.assertEqual(
            [item["local"] for item in resultado["sequencia"]],
            ["ubs", "Hospital"],
        )
        self.assertTrue(any("duplicado" in aviso for aviso in resultado["avisos"]))
        self.assertTrue(any("sem local" in aviso for aviso in resultado["avisos"]))

    def test_vizinho_mais_proximo_deixa_ponto_inalcancavel(self):
        resultado = calcular_itinerario(
            [
                {"local": "A", "ordem": 1},
                {"local": "C", "ordem": 2},
                {"local": "B", "ordem": 3},
            ],
            distancias={("A", "B"): 1},
        )
        self.assertEqual([item["local"] for item in resultado["sequencia"]], ["A", "B"])
        self.assertEqual(resultado["distancia_total_km"], 1)
        self.assertTrue(any("inalcançável" in aviso for aviso in resultado["avisos"]))


class AcessoTests(TestCase):
    def test_anonimo_vai_para_o_login(self):
        resposta = self.client.get("/rotas/")
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/entrar/", resposta["Location"])

    def test_atendente_nao_apaga_veiculo(self):
        entrar(self.client)
        marca = Marca.objects.create(nome="Ford")
        modelo = Modelo.objects.create(nome="Transit", marca=marca)
        veiculo = Veiculo.objects.create(
            placa="ATD1C23",
            modelo=modelo,
            ano=2020,
            chassi="99999999999999999",
            renavam="99999999999",
            capacidade=5,
        )
        resposta = self.client.post(f"/Veiculo/{veiculo.pk}/apagar/")
        self.assertEqual(resposta.status_code, 403)
        self.assertTrue(Veiculo.objects.filter(pk=veiculo.pk).exists())

    def test_painel_do_admin_mostra_o_agendamento(self):
        entrar(self.client, "admin@rotasaude.com.br")
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Novo agendamento")
        self.assertContains(resposta, "Despacho rápido")
