from datetime import time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from contas.models import Perfil, Usuario

from .forms import MotoristaForm, PedidoPontoForm, PontoEmbarqueForm, VeiculoForm
from .models import Marca, Modelo, Motorista, PedidoPontoEmbarque, PontoEmbarque, Veiculo
from .validadores import cpf_valido, formatar_placa, mascarar_cpf, validar_chassi, validar_cpf

CPFS_VALIDOS = ["12345678143", "23456789254", "34567890337", "45678901400", "56789012575", "67890123620"]


def criar_usuario(email, perfil=Perfil.ATENDENTE):
    return Usuario.objects.create_user(username=email, email=email, password="senha123", nome=email.split("@")[0].title(), perfil=perfil)


def criar_modelo(nome="Sprinter", marca="Mercedes-Benz"):
    marca_obj, _ = Marca.objects.get_or_create(nome=marca)
    modelo, _ = Modelo.objects.get_or_create(nome=nome, marca=marca_obj)
    return modelo


def criar_veiculo(placa="ABC1D23", chassi="9BWZZZ377VT004251", capacidade=12, status=Veiculo.Status.DISPONIVEL, modelo=None):
    return Veiculo.objects.create(
        modelo=modelo or criar_modelo(), placa=placa, chassi=chassi, ano=2022, capacidade=capacidade, status=status
    )


def criar_motorista(nome="Carlos Eduardo Mendes", cpf="12345678143", cnh="01234501111", validade_dias=365):
    return Motorista.objects.create(
        nome=nome, cpf=cpf, cnh=cnh, categoria_cnh="D",
        validade_cnh=timezone.localdate() + timedelta(days=validade_dias),
    )


def dados_veiculo(**extras):
    dados = {
        "tipo": "van", "modelo": criar_modelo().pk, "placa": "ABC-1D23", "chassi": "9bwzzz377vt004251",
        "renavam": "", "ano": "2022", "capacidade": "12",
    }
    dados.update(extras)
    return dados


def dados_motorista(**extras):
    dados = {
        "nome": "Ana Paula Ferreira", "cpf": "234.567.892-54", "cnh": "01234502222", "categoria_cnh": "D",
        "validade_cnh": (timezone.localdate() + timedelta(days=200)).isoformat(), "telefone": "", "curso_emergencia": "on",
    }
    dados.update(extras)
    return dados


class ValidadoresTests(TestCase):
    def test_cpfs_de_teste_sao_validos(self):
        for cpf in CPFS_VALIDOS:
            self.assertTrue(cpf_valido(cpf), cpf)
        validar_cpf("123.456.781-43")

    def test_cpf_repetido_ou_errado_e_invalido(self):
        self.assertFalse(cpf_valido("11111111111"))
        self.assertFalse(cpf_valido("12345678900"))
        with self.assertRaises(ValidationError):
            validar_cpf("1234")

    def test_mascara_do_cpf(self):
        self.assertEqual(mascarar_cpf("12345678143"), "***.456.781-**")

    def test_chassi_com_i_o_q_ou_tamanho_errado_e_invalido(self):
        validar_chassi("9BWZZZ377VT004251")
        for errado in ("9BWZZZ377VT00425I", "9BWZZZ377VT00425O", "9BWZZZ377VT00425Q", "9BWZZZ377VT0042"):
            with self.assertRaises(ValidationError):
                validar_chassi(errado)

    def test_placa_formatada(self):
        self.assertEqual(formatar_placa("abc1d23"), "ABC-1D23")


class VeiculoFormTests(TestCase):
    def test_placa_com_hifen_e_normalizada(self):
        form = VeiculoForm(dados_veiculo())
        self.assertTrue(form.is_valid(), form.errors)
        veiculo = form.save()
        self.assertEqual(veiculo.placa, "ABC1D23")
        self.assertEqual(veiculo.chassi, "9BWZZZ377VT004251")
        self.assertIsNone(veiculo.renavam)

    def test_placa_repetida_com_ou_sem_hifen_nao_grava(self):
        criar_veiculo(placa="ABC1D23")
        form = VeiculoForm(dados_veiculo(placa="abc-1d23", chassi="93ZC3570ABC123456"))
        self.assertFalse(form.is_valid())
        self.assertIn("placa", form.errors)

    def test_placa_fora_do_formato_nao_grava(self):
        form = VeiculoForm(dados_veiculo(placa="AB-12345"))
        self.assertFalse(form.is_valid())
        self.assertIn("placa", form.errors)

    def test_chassi_invalido_nao_grava(self):
        form = VeiculoForm(dados_veiculo(chassi="9BWZZZ377VT00425I"))
        self.assertFalse(form.is_valid())
        self.assertIn("chassi", form.errors)

    def test_capacidade_fora_do_limite_nao_grava(self):
        form = VeiculoForm(dados_veiculo(capacidade="61"))
        self.assertFalse(form.is_valid())
        self.assertIn("capacidade", form.errors)


class MotoristaFormTests(TestCase):
    def test_cadastro_valido_guarda_so_digitos(self):
        form = MotoristaForm(dados_motorista())
        self.assertTrue(form.is_valid(), form.errors)
        motorista = form.save()
        self.assertEqual(motorista.cpf, "23456789254")
        self.assertTrue(motorista.cnh_valida())

    def test_cnh_vencida_bloqueia_cadastro_novo(self):
        ontem = (timezone.localdate() - timedelta(days=1)).isoformat()
        form = MotoristaForm(dados_motorista(validade_cnh=ontem))
        self.assertFalse(form.is_valid())
        self.assertIn("CNH vencida. Não é possível cadastrar.", form.errors["validade_cnh"])

    def test_cpf_invalido_nao_grava(self):
        form = MotoristaForm(dados_motorista(cpf="111.111.111-11"))
        self.assertFalse(form.is_valid())
        self.assertIn("cpf", form.errors)

    def test_nome_repetido_sem_diferenciar_maiusculas(self):
        criar_motorista(nome="Ana Paula Ferreira", cpf="34567890337", cnh="01234503333")
        form = MotoristaForm(dados_motorista(nome="ana paula ferreira"))
        self.assertFalse(form.is_valid())
        self.assertIn("Esse motorista já está cadastrado.", str(form.errors))

    def test_cnh_vencida_no_dia_da_viagem(self):
        motorista = criar_motorista(validade_dias=5)
        self.assertTrue(motorista.cnh_valida())
        self.assertFalse(motorista.cnh_valida(timezone.localdate() + timedelta(days=6)))


class PontosTests(TestCase):
    def setUp(self):
        self.admin = criar_usuario("admin@rotasaude.com.br", Perfil.ADMIN)
        self.client.force_login(self.admin)

    def test_remover_desativa_ponto(self):
        ponto = PontoEmbarque.objects.get(nome="UBS Centro")
        resposta = self.client.post(reverse("frota:remover_ponto", args=[ponto.pk]))
        self.assertRedirects(resposta, reverse("frota:pontos"), fetch_redirect_response=False)
        ponto.refresh_from_db()
        self.assertFalse(ponto.ativo)

    def test_mantem_pelo_menos_um_ponto(self):
        PontoEmbarque.objects.exclude(nome="UBS Centro").update(ativo=False)
        ponto = PontoEmbarque.objects.get(nome="UBS Centro")
        self.client.post(reverse("frota:remover_ponto", args=[ponto.pk]))
        ponto.refresh_from_db()
        self.assertTrue(ponto.ativo)

    def test_cadastrar_de_novo_ponto_removido_reativa(self):
        ponto = PontoEmbarque.objects.get(nome="UBS Centro")
        ponto.ativo = False
        ponto.save()
        form = PontoEmbarqueForm({"nome": "ubs centro", "endereco": "Rua Nova, 10, Centro", "cep": "15400000"})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        ponto.refresh_from_db()
        self.assertTrue(ponto.ativo)
        self.assertEqual(ponto.cep, "15400-000")
        self.assertEqual(PontoEmbarque.objects.filter(nome__iexact="ubs centro").count(), 1)

    def test_nome_repetido_ativo_nao_grava(self):
        form = PontoEmbarqueForm({"nome": "UBS CENTRO", "endereco": "Rua Nova, 10", "cep": ""})
        self.assertFalse(form.is_valid())

    def test_cep_invalido_nao_grava(self):
        form = PontoEmbarqueForm({"nome": "UBS Vila Nova", "endereco": "Rua Nova, 10", "cep": "1540"})
        self.assertFalse(form.is_valid())
        self.assertIn("cep", form.errors)


class PedidoPontoTests(TestCase):
    def setUp(self):
        self.admin = criar_usuario("admin@rotasaude.com.br", Perfil.ADMIN)
        self.atendente = criar_usuario("atendente@rotasaude.com.br")

    def _pedir(self):
        self.client.force_login(self.atendente)
        return self.client.post(reverse("frota:solicitar_ponto"), {
            "nome": "UBS Vila Nova", "endereco": "Rua das Flores, 120, Vila Nova", "cep": "", "justificativa": "",
        })

    def test_atendente_envia_e_admin_aprova(self):
        resposta = self._pedir()
        self.assertRedirects(resposta, reverse("frota:solicitar_ponto"), fetch_redirect_response=False)
        pedido = PedidoPontoEmbarque.objects.get()
        self.assertEqual(pedido.solicitante, self.atendente)
        self.client.force_login(self.admin)
        self.client.post(reverse("frota:aprovar_pedido", args=[pedido.pk]))
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, PedidoPontoEmbarque.Status.APROVADO)
        self.assertEqual(pedido.respondido_por, self.admin)
        self.assertTrue(PontoEmbarque.objects.filter(nome="UBS Vila Nova", ativo=True).exists())

    def test_atendente_nao_aprova(self):
        self._pedir()
        pedido = PedidoPontoEmbarque.objects.get()
        resposta = self.client.post(reverse("frota:aprovar_pedido", args=[pedido.pk]))
        self.assertEqual(resposta.status_code, 403)

    def test_recusa_exige_motivo(self):
        self._pedir()
        pedido = PedidoPontoEmbarque.objects.get()
        self.client.force_login(self.admin)
        self.client.post(reverse("frota:recusar_pedido", args=[pedido.pk]), {"motivo": "não"})
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, PedidoPontoEmbarque.Status.PENDENTE)
        self.client.post(reverse("frota:recusar_pedido", args=[pedido.pk]), {"motivo": "Já existe um ponto próximo"})
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, PedidoPontoEmbarque.Status.RECUSADO)
        self.assertEqual(pedido.motivo_recusa, "Já existe um ponto próximo")

    def test_pedido_repetido_ou_ponto_existente_nao_grava(self):
        self._pedir()
        form = PedidoPontoForm({"nome": "ubs vila nova", "endereco": "Rua X, 1, Centro"})
        self.assertFalse(form.is_valid())
        form = PedidoPontoForm({"nome": "UBS Centro", "endereco": "Rua X, 1, Centro"})
        self.assertFalse(form.is_valid())


class VeiculoViewsTests(TestCase):
    def setUp(self):
        self.admin = criar_usuario("admin@rotasaude.com.br", Perfil.ADMIN)
        self.client.force_login(self.admin)

    def test_apagar_veiculo_com_viagem_e_protegido(self):
        from viagens.models import Viagem

        veiculo = criar_veiculo()
        Viagem.objects.create(
            veiculo=veiculo, motorista=criar_motorista(), data=timezone.localdate(), saida=time(7, 0),
            duracao_horas=2, destino="Barretos", criado_por=self.admin,
        )
        resposta = self.client.post(reverse("frota:apagar_veiculo", args=[veiculo.pk]))
        self.assertRedirects(resposta, reverse("frota:veiculos"), fetch_redirect_response=False)
        self.assertTrue(Veiculo.objects.filter(pk=veiculo.pk).exists())
        mensagens = [str(m) for m in resposta.wsgi_request._messages]
        self.assertTrue(any("não pode ser apagado" in m for m in mensagens))

    def test_apagar_veiculo_sem_viagem(self):
        veiculo = criar_veiculo()
        self.client.post(reverse("frota:apagar_veiculo", args=[veiculo.pk]))
        self.assertFalse(Veiculo.objects.filter(pk=veiculo.pk).exists())

    def test_mudar_status(self):
        veiculo = criar_veiculo()
        self.client.post(reverse("frota:status_veiculo", args=[veiculo.pk]), {"status": "manutencao"})
        veiculo.refresh_from_db()
        self.assertTrue(veiculo.em_manutencao)
        self.client.post(reverse("frota:status_veiculo", args=[veiculo.pk]), {"status": "inventado"})
        veiculo.refresh_from_db()
        self.assertEqual(veiculo.status, "manutencao")

    def test_atendente_sem_frota_recebe_403(self):
        self.client.force_login(criar_usuario("at@rotasaude.com.br"))
        self.assertEqual(self.client.get(reverse("frota:veiculos")).status_code, 403)
