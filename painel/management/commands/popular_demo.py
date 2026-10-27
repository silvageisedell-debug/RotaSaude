from datetime import time, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from contas.demo import CONTAS_DEMO
from contas.models import Usuario
from frota.models import Marca, Modelo, Motorista, PontoEmbarque, Veiculo
from solicitacoes.models import Categoria, Destino, Solicitacao
from viagens import services

VEICULOS = [
    # tipo, marca, modelo, placa, chassi, ano, lugares, status
    ("van", "Mercedes-Benz", "Sprinter", "ABC1D23", "9BWZZZ377VT004251", 2022, 12, "disponivel"),
    ("micro_onibus", "Volare", "W9", "DEF4G56", "93ZC3570ABC123456", 2021, 20, "disponivel"),
    ("carro", "Fiat", "Doblò Adaptado", "GHI7J89", "9BD27805JA7123456", 2019, 4, "manutencao"),
    ("ambulancia", "Mercedes-Benz", "Sprinter UTI", "JKL2M34", "9BM3665571B123456", 2023, 3, "disponivel"),
    ("ambulancia", "Renault", "Master Simples", "MNO5P67", "93YMAF4XHKJ234567", 2022, 3, "disponivel"),
    ("carro", "Fiat", "Cronos", "PQR8S90", "9BD359115L1345678", 2024, 4, "disponivel"),
    ("carro", "Chevrolet", "Onix", "STU1V23", "9BGKS48T0LG456789", 2024, 4, "disponivel"),
]

# CPFs fictícios, mas com dígitos verificadores válidos.
MOTORISTAS = [
    ("Carlos Eduardo Mendes", "12345678143", "01234501111", "D", 900, "(17) 90000-0001", True),
    ("Ana Paula Ferreira", "23456789254", "01234502222", "D", 1400, "(17) 90000-0002", True),
    ("Roberto Alves Lima", "34567890337", "01234503333", "E", 760, "(17) 90000-0003", True),
    ("Fernanda Costa Rocha", "45678901400", "01234504444", "D", 1550, "(17) 90000-0004", False),
    ("Marcelo Santos Pereira", "56789012575", "01234505555", "B", 20, "(17) 90000-0005", True),
    ("José Antônio Barbosa", "67890123620", "01234506666", "D", -30, "(17) 90000-0006", True),
]


class Command(BaseCommand):
    help = "Popula o banco com os dados de apresentação do protótipo (contas, frota, solicitações e viagens)."

    @transaction.atomic
    def handle(self, *args, **options):
        hoje = timezone.localdate()
        usuarios = {}
        for conta in CONTAS_DEMO:
            usuario, criado = Usuario.objects.get_or_create(
                email=conta["email"],
                defaults={"nome": conta["nome"], "perfil": conta["perfil"], "username": conta["email"]},
            )
            if criado:
                usuario.set_password(conta["senha"])
                if conta["perfil"] == "admin":
                    usuario.is_staff = usuario.is_superuser = True
                usuario.save()
            usuarios[conta["perfil"]] = usuario

        for tipo, marca, modelo, placa, chassi, ano, lugares, status in VEICULOS:
            marca_obj, _ = Marca.objects.get_or_create(nome=marca)
            modelo_obj, _ = Modelo.objects.get_or_create(nome=modelo, marca=marca_obj)
            Veiculo.objects.get_or_create(placa=placa, defaults={
                "tipo": tipo, "modelo": modelo_obj, "chassi": chassi, "ano": ano,
                "capacidade": lugares, "status": status,
            })

        for nome, cpf, cnh, categoria, dias, telefone, curso in MOTORISTAS:
            Motorista.objects.get_or_create(cpf=cpf, defaults={
                "nome": nome, "cnh": cnh, "categoria_cnh": categoria,
                "validade_cnh": hoje + timedelta(days=dias), "telefone": telefone, "curso_emergencia": curso,
            })

        if Solicitacao.objects.exists():
            self.stdout.write(self.style.WARNING("Já existem solicitações: só contas e frota foram conferidas."))
            return

        atendente = usuarios["atendente"]
        ponto = {p.nome: p for p in PontoEmbarque.objects.all()}
        destino = {d.cidade: d for d in Destino.objects.all()}
        categoria = {c.nome: c for c in Categoria.objects.all()}

        def nova(paciente, tipo, embarque, cidade, dias, hora, acompanhante, status, cat="Eletiva"):
            s = Solicitacao.objects.create(
                paciente=paciente, tipo=tipo, ponto_embarque=ponto[embarque], destino=destino[cidade],
                categoria=categoria[cat], data=hoje + timedelta(days=dias), horario=hora,
                acompanhante=acompanhante, status=status, criado_por=atendente,
            )
            s.registrar(f"Registrada pelo atendimento ({atendente.nome}).", atendente)
            return s

        s1 = nova("Maria das Dores Souza", "hemodialise", "UBS Centro", "São José do Rio Preto", 0, time(6, 30), False, "aprovada", "Prioritária")
        s2 = nova("José Almeida", "consulta", "Residência do paciente", "Barretos", 0, time(8, 0), True, "aprovada", "Urgente")
        nova("Ana Paula Ribeiro", "exame", "UBS Jardim Santa Rosa", "Ribeirão Preto", 1, time(7, 0), False, "pendente")
        nova("Carlos Eduardo Lima", "cirurgia", "Rodoviária de Olímpia", "São José do Rio Preto", 2, time(6, 0), True, "aprovada", "Urgente")
        nova("Maria das Dores Souza", "consulta", "UBS Centro", "Ribeirão Preto", 3, time(9, 0), False, "pendente")
        nova("Pedro Henrique Dias", "fisioterapia", "UBS Centro", "Barretos", 1, time(7, 30), False, "pendente")

        van = Veiculo.objects.get(placa="ABC1D23")
        micro = Veiculo.objects.get(placa="DEF4G56")
        carlos = Motorista.objects.get(cpf="12345678143")
        ana = Motorista.objects.get(cpf="23456789254")
        services.programar_viagem(
            data=hoje, saida=time(6, 0), duracao_horas=6, veiculo=van, motorista=carlos,
            solicitacoes=[s1], usuario=atendente,
        )
        segunda = services.programar_viagem(
            data=hoje, saida=time(8, 0), duracao_horas=7, veiculo=micro, motorista=ana,
            solicitacoes=[s2], usuario=atendente,
        )
        services.iniciar_viagem(segunda, atendente)

        self.stdout.write(self.style.SUCCESS(
            "Dados de demonstração criados. Entre com admin@rotasaude.com.br / admin123 "
            "ou atendente@rotasaude.com.br / atend123."
        ))
