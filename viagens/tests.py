from datetime import time, timedelta

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from contas.models import Perfil, Usuario
from frota.models import Marca, Modelo, Motorista, PontoEmbarque, Veiculo
from solicitacoes.models import Categoria, Destino, Solicitacao

from . import services
from .models import Parada, Viagem


class Base(TestCase):
    """Frota com dois veículos e dois motoristas, e uma atendente logada."""

    def setUp(self):
        self.hoje = timezone.localdate()
        self.usuario = Usuario.objects.create_user(
            username="at@rotasaude.com.br", email="at@rotasaude.com.br", password="senha123",
            nome="Rafael Atendente", perfil=Perfil.ATENDENTE,
        )
        marca = Marca.objects.create(nome="Mercedes-Benz")
        modelo = Modelo.objects.create(nome="Sprinter", marca=marca)
        self.van = Veiculo.objects.create(modelo=modelo, placa="ABC1D23", chassi="9BWZZZ377VT004251", ano=2022, capacidade=3)
        self.carro = Veiculo.objects.create(modelo=modelo, placa="PQR8S90", chassi="9BD359115L1345678", ano=2024, capacidade=4)
        self.carlos = Motorista.objects.create(
            nome="Carlos Mendes", cpf="12345678143", cnh="01234501111", validade_cnh=self.hoje + timedelta(days=300)
        )
        self.ana = Motorista.objects.create(
            nome="Ana Ferreira", cpf="23456789254", cnh="01234502222", validade_cnh=self.hoje + timedelta(days=300)
        )
        self.ubs = PontoEmbarque.objects.get(nome="UBS Centro")
        self.rodoviaria = PontoEmbarque.objects.get(nome="Rodoviária de Olímpia")
        self.barretos = Destino.objects.get(cidade="Barretos")

    def solicitacao(self, paciente="Maria", status=Solicitacao.Status.APROVADA, data=None, acompanhante=False,
                    ponto=None, horario=time(7, 0), destino=None):
        return Solicitacao.objects.create(
            paciente=paciente, categoria=Categoria.objects.get(nome="Eletiva"), ponto_embarque=ponto or self.ubs,
            destino=destino or self.barretos, data=data or self.hoje, horario=horario, acompanhante=acompanhante,
            status=status, criado_por=self.usuario,
        )

    def programar(self, solicitacoes=None, saida=time(7, 0), duracao=3, veiculo=None, motorista=None, data=None):
        return services.programar_viagem(
            data=data or self.hoje, saida=saida, duracao_horas=duracao, veiculo=veiculo or self.van,
            motorista=motorista or self.carlos, solicitacoes=solicitacoes or [self.solicitacao()], usuario=self.usuario,
        )

    def erros(self, solicitacoes=None, saida=time(7, 0), duracao=3, veiculo=None, motorista=None, data=None):
        return services.validar_programacao(
            data or self.hoje, saida, duracao, veiculo or self.van, motorista or self.carlos,
            solicitacoes if solicitacoes is not None else [self.solicitacao()],
        )


class DisponibilidadeTests(Base):
    def _status(self, situacao, objeto):
        return next(s.status for s in situacao if s.objeto.pk == objeto.pk)

    def test_visao_do_dia(self):
        self.carro.status = Veiculo.Status.MANUTENCAO
        self.carro.save()
        self.ana.validade_cnh = self.hoje - timedelta(days=1)
        self.ana.save()
        d = services.disponibilidade(self.hoje)
        self.assertEqual(self._status(d["veiculos"], self.van), services.DISPONIVEL)
        self.assertEqual(self._status(d["veiculos"], self.carro), services.MANUTENCAO)
        self.assertEqual(self._status(d["motoristas"], self.carlos), services.DISPONIVEL)
        self.assertEqual(self._status(d["motoristas"], self.ana), services.CNH_VENCIDA)

    def test_programado_e_em_viagem(self):
        viagem = self.programar()
        d = services.disponibilidade(self.hoje)
        self.assertEqual(self._status(d["veiculos"], self.van), services.PROGRAMADO)
        self.assertEqual(self._status(d["motoristas"], self.carlos), services.PROGRAMADO)
        services.iniciar_viagem(viagem, self.usuario)
        d = services.disponibilidade(self.hoje)
        self.assertEqual(self._status(d["veiculos"], self.van), services.EM_VIAGEM)
        self.assertEqual(self._status(d["motoristas"], self.carlos), services.EM_VIAGEM)

    def test_visao_por_janela_mostra_ocupado(self):
        self.programar(saida=time(7, 0), duracao=3)
        d = services.disponibilidade(self.hoje, time(9, 0), 2)
        self.assertEqual(self._status(d["veiculos"], self.van), services.OCUPADO)
        self.assertEqual(self._status(d["motoristas"], self.carlos), services.OCUPADO)
        self.assertEqual(self._status(d["veiculos"], self.carro), services.DISPONIVEL)
        d = services.disponibilidade(self.hoje, time(10, 0), 2)
        self.assertEqual(self._status(d["veiculos"], self.van), services.DISPONIVEL)

    def test_viagem_cancelada_libera(self):
        viagem = self.programar()
        services.cancelar_viagem(viagem, self.usuario)
        d = services.disponibilidade(self.hoje, time(7, 0), 3)
        self.assertEqual(self._status(d["veiculos"], self.van), services.DISPONIVEL)


class ValidarProgramacaoTests(Base):
    def test_caso_valido_nao_tem_erros(self):
        self.assertEqual(self.erros(), [])

    def test_sem_pacientes(self):
        self.assertIn("Marque ao menos um paciente.", self.erros(solicitacoes=[]))

    def test_capacidade_conta_acompanhante(self):
        pacientes = [self.solicitacao("A", acompanhante=True), self.solicitacao("B", acompanhante=True)]
        erros = self.erros(solicitacoes=pacientes)
        self.assertTrue(any("acima da capacidade" in e for e in erros))
        self.assertEqual(self.erros(solicitacoes=pacientes, veiculo=self.carro), [])

    def test_conflito_de_veiculo(self):
        self.programar(saida=time(7, 0), duracao=3)
        erros = self.erros(solicitacoes=[self.solicitacao("B")], saida=time(9, 0), motorista=self.ana)
        self.assertTrue(any("Conflito: o veículo" in e for e in erros))

    def test_conflito_de_motorista(self):
        self.programar(saida=time(7, 0), duracao=3)
        erros = self.erros(solicitacoes=[self.solicitacao("B")], saida=time(8, 0), veiculo=self.carro)
        self.assertTrue(any("Conflito: o motorista" in e for e in erros))

    def test_viagens_encostadas_nao_conflitam(self):
        self.programar(saida=time(7, 0), duracao=3)
        self.assertEqual(self.erros(solicitacoes=[self.solicitacao("B")], saida=time(10, 0)), [])

    def test_cnh_vencida_na_data(self):
        self.carlos.validade_cnh = self.hoje - timedelta(days=1)
        self.carlos.save()
        self.assertTrue(any("CNH" in e for e in self.erros()))

    def test_veiculo_em_manutencao(self):
        self.van.status = Veiculo.Status.MANUTENCAO
        self.van.save()
        self.assertIn("Este veículo está em manutenção.", self.erros())

    def test_janela_de_operacao(self):
        self.assertTrue(any("terminar até" in e for e in self.erros(saida=time(4, 30))))
        self.assertTrue(any("terminar até" in e for e in self.erros(saida=time(18, 0), duracao=3)))
        self.assertEqual(self.erros(saida=time(17, 0), duracao=3), [])
        self.assertTrue(any("1 a 12 horas" in e for e in self.erros(duracao=13)))

    def test_data_da_solicitacao_diferente(self):
        amanha = self.hoje + timedelta(days=1)
        erros = self.erros(solicitacoes=[self.solicitacao(data=amanha)])
        self.assertTrue(any("Programe a viagem nessa data" in e for e in erros))

    def test_status_que_nao_aguarda_viagem(self):
        for status in (Solicitacao.Status.NEGADA, Solicitacao.Status.AGENDADA, Solicitacao.Status.CONCLUIDA):
            erros = self.erros(solicitacoes=[self.solicitacao(status=status)])
            self.assertTrue(any("não está aguardando viagem" in e for e in erros), status)
        self.assertEqual(self.erros(solicitacoes=[self.solicitacao(status=Solicitacao.Status.PENDENTE)]), [])

    def test_data_passada(self):
        ontem = self.hoje - timedelta(days=1)
        erros = self.erros(solicitacoes=[self.solicitacao(data=ontem)], data=ontem)
        self.assertIn("A data da viagem não pode ser anterior a hoje.", erros)

    def test_programar_com_erro_levanta_value_error(self):
        self.van.status = Veiculo.Status.MANUTENCAO
        self.van.save()
        with self.assertRaises(ValueError):
            self.programar()
        self.assertEqual(Viagem.objects.count(), 0)


class ProgramarTests(Base):
    def test_programar_agenda_pacientes_e_monta_itinerario(self):
        rio_preto = Destino.objects.get(cidade="São José do Rio Preto")
        a = self.solicitacao("A", ponto=self.rodoviaria, horario=time(8, 0))
        b = self.solicitacao("B", ponto=self.ubs, horario=time(6, 30), destino=rio_preto)
        viagem = self.programar(solicitacoes=[a, b])
        for s in (a, b):
            s.refresh_from_db()
            self.assertEqual(s.status, Solicitacao.Status.AGENDADA)
            self.assertEqual(s.viagem, viagem)
            self.assertIn("Aceita por Rafael Atendente", s.historico.last().texto)
        paradas = list(viagem.paradas.values_list("ordem", "local"))
        self.assertEqual([o for o, _ in paradas], [1, 2, 3, 4])
        self.assertEqual(paradas[0][1], "UBS Centro")
        self.assertEqual(paradas[1][1], "Rodoviária de Olímpia")
        self.assertEqual({l for _, l in paradas[2:]}, {str(self.barretos), str(rio_preto)})
        self.assertEqual(viagem.status, Viagem.Status.PROGRAMADA)

    def test_parada_ordem_unica_na_viagem(self):
        viagem = self.programar()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Parada.objects.create(viagem=viagem, ordem=1, local="Outro")

    def test_protect_em_veiculo_e_motorista(self):
        self.programar()
        with self.assertRaises(ProtectedError):
            self.van.delete()
        with self.assertRaises(ProtectedError):
            self.carlos.delete()

    def test_gantt_e_chegada(self):
        viagem = self.programar(saida=time(8, 0), duracao=3)
        self.assertEqual(viagem.chegada, time(11, 0))
        self.assertEqual(viagem.gantt_esquerda, 20.0)
        self.assertEqual(viagem.gantt_largura, 20.0)


class ExecucaoTests(Base):
    def setUp(self):
        super().setUp()
        self.a = self.solicitacao("A")
        self.b = self.solicitacao("B")
        self.viagem = self.programar(solicitacoes=[self.a, self.b])

    def test_iniciar_coloca_em_viagem(self):
        services.iniciar_viagem(self.viagem, self.usuario)
        self.viagem.refresh_from_db()
        self.van.refresh_from_db()
        self.a.refresh_from_db()
        self.assertEqual(self.viagem.status, Viagem.Status.EM_ANDAMENTO)
        self.assertEqual(self.van.status, Veiculo.Status.EM_VIAGEM)
        self.assertEqual(self.a.status, Solicitacao.Status.EM_VIAGEM)
        with self.assertRaises(ValueError):
            services.iniciar_viagem(self.viagem, self.usuario)

    def test_embarque_so_com_viagem_em_andamento(self):
        with self.assertRaises(ValueError):
            services.alternar_embarque(self.viagem, self.a)
        services.iniciar_viagem(self.viagem, self.usuario)
        self.a.refresh_from_db()
        self.assertTrue(services.alternar_embarque(self.viagem, self.a))
        self.assertFalse(services.alternar_embarque(self.viagem, self.a))

    def test_concluir_separa_quem_embarcou(self):
        services.iniciar_viagem(self.viagem, self.usuario)
        self.a.refresh_from_db()
        services.alternar_embarque(self.viagem, self.a)
        services.concluir_viagem(self.viagem, self.usuario)
        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.van.refresh_from_db()
        self.assertEqual(self.a.status, Solicitacao.Status.CONCLUIDA)
        self.assertEqual(self.b.status, Solicitacao.Status.APROVADA)
        self.assertIsNone(self.b.viagem)
        self.assertEqual(self.van.status, Veiculo.Status.DISPONIVEL)

    def test_concluir_viagem_programada_falha(self):
        with self.assertRaises(ValueError):
            services.concluir_viagem(self.viagem, self.usuario)

    def test_cancelar_devolve_pacientes(self):
        services.cancelar_viagem(self.viagem, self.usuario)
        self.viagem.refresh_from_db()
        self.assertEqual(self.viagem.status, Viagem.Status.CANCELADA)
        for s in (self.a, self.b):
            s.refresh_from_db()
            self.assertEqual(s.status, Solicitacao.Status.APROVADA)
            self.assertIsNone(s.viagem)

    def test_cancelar_em_andamento_falha(self):
        services.iniciar_viagem(self.viagem, self.usuario)
        with self.assertRaises(ValueError):
            services.cancelar_viagem(self.viagem, self.usuario)


class ViewsTests(Base):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.usuario)

    def test_disponibilidade_json(self):
        self.programar(saida=time(7, 0), duracao=3)
        resposta = self.client.get(reverse("viagens:disponibilidade"), {
            "data": self.hoje.isoformat(), "saida": "08:00", "duracao": "2",
        })
        self.assertEqual(resposta.status_code, 200)
        dados = resposta.json()
        van = next(v for v in dados["veiculos"] if v["id"] == self.van.pk)
        self.assertFalse(van["livre"])
        self.assertEqual(van["status"], services.OCUPADO)
        ana = next(m for m in dados["motoristas"] if m["id"] == self.ana.pk)
        self.assertTrue(ana["livre"])

    def test_programar_post_redireciona_para_quadro(self):
        s = self.solicitacao()
        resposta = self.client.post(reverse("viagens:programar"), {
            "data": self.hoje.isoformat(), "saida": "07:00", "duracao_horas": "3",
            "veiculo": self.van.pk, "motorista": self.carlos.pk, "solicitacoes": [s.pk],
        })
        viagem = Viagem.objects.get()
        self.assertRedirects(
            resposta, f"{reverse('viagens:quadro')}?data={self.hoje.isoformat()}", fetch_redirect_response=False
        )
        self.assertEqual(viagem.passageiros.get(), s)

    def test_acoes_exigem_post(self):
        viagem = self.programar()
        self.assertEqual(self.client.get(reverse("viagens:iniciar", args=[viagem.pk])).status_code, 405)
        resposta = self.client.post(reverse("viagens:iniciar", args=[viagem.pk]))
        self.assertRedirects(resposta, reverse("viagens:detalhe", args=[viagem.pk]), fetch_redirect_response=False)
        viagem.refresh_from_db()
        self.assertEqual(viagem.status, Viagem.Status.EM_ANDAMENTO)

    def test_embarque_view(self):
        viagem = self.programar()
        services.iniciar_viagem(viagem, self.usuario)
        s = viagem.passageiros.get()
        self.client.post(reverse("viagens:embarque", args=[viagem.pk, s.pk]))
        s.refresh_from_db()
        self.assertTrue(s.embarcou)

    def test_sem_permissao_de_viagens(self):
        aux = Usuario.objects.create_user(
            username="aux@x.com", email="aux@x.com", password="senha123", nome="Aux", perfil=Perfil.AUXADM
        )
        from contas.models import PermissaoModulo

        PermissaoModulo.objects.filter(perfil="auxadm", modulo="viagens").delete()
        self.client.force_login(aux)
        self.assertEqual(self.client.get(reverse("viagens:disponibilidade")).status_code, 403)
