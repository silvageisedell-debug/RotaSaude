from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from .validadores import (
    formatar_cep,
    formatar_placa,
    mascarar_cpf,
    validar_cep,
    validar_chassi,
    validar_cnh,
    validar_cpf,
    validar_placa,
)


class Marca(models.Model):
    nome = models.CharField("Nome da marca", max_length=50, unique=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Modelo(models.Model):
    nome = models.CharField("Nome do modelo", max_length=50)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name="modelos")

    class Meta:
        verbose_name = "Modelo"
        verbose_name_plural = "Modelos"
        ordering = ["marca__nome", "nome"]
        constraints = [
            models.UniqueConstraint(fields=["marca", "nome"], name="frota_modelo_unico_na_marca"),
        ]

    def __str__(self):
        return f"{self.marca.nome} {self.nome}"


class Veiculo(models.Model):
    class Tipo(models.TextChoices):
        AMBULANCIA = "ambulancia", "Ambulância"
        VAN = "van", "Van"
        MICRO_ONIBUS = "micro_onibus", "Micro-ônibus"
        CARRO = "carro", "Carro"

    class Status(models.TextChoices):
        DISPONIVEL = "disponivel", "Disponível"
        EM_VIAGEM = "em_viagem", "Em viagem"
        MANUTENCAO = "manutencao", "Manutenção"

    tipo = models.CharField("Tipo", max_length=20, choices=Tipo.choices, default=Tipo.VAN)
    modelo = models.ForeignKey(Modelo, on_delete=models.PROTECT, related_name="veiculos")
    placa = models.CharField("Placa", max_length=7, unique=True, validators=[validar_placa])
    chassi = models.CharField("Chassi", max_length=17, unique=True, validators=[validar_chassi])
    renavam = models.CharField("Renavam", max_length=11, unique=True, null=True, blank=True)
    ano = models.PositiveIntegerField("Ano de fabricação", validators=[MinValueValidator(1950)])
    # Lugares para pacientes e acompanhantes, sem contar o motorista.
    capacidade = models.PositiveIntegerField(
        "Lugares", validators=[MinValueValidator(1), MaxValueValidator(60)]
    )
    status = models.CharField("Status", max_length=20, choices=Status.choices, default=Status.DISPONIVEL)

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        ordering = ["modelo__marca__nome", "modelo__nome", "placa"]

    def __str__(self):
        return f"{self.modelo} ({self.placa_formatada})"

    @property
    def placa_formatada(self):
        return formatar_placa(self.placa)

    @property
    def em_manutencao(self):
        return self.status == self.Status.MANUTENCAO


class Motorista(models.Model):
    class Categoria(models.TextChoices):
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"
        E = "E", "E"

    nome = models.CharField("Nome completo", max_length=60)
    cpf = models.CharField("CPF", max_length=11, unique=True, validators=[validar_cpf])
    cnh = models.CharField("Nº da CNH", max_length=11, unique=True, validators=[validar_cnh])
    categoria_cnh = models.CharField("Categoria", max_length=1, choices=Categoria.choices, default=Categoria.D)
    validade_cnh = models.DateField("Validade da CNH")
    telefone = models.CharField("Telefone", max_length=16, blank=True)
    curso_emergencia = models.BooleanField("Tem o curso de condutor de veículo de emergência", default=False)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Motorista"
        verbose_name_plural = "Motoristas"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                Lower("nome"),
                name="frota_motorista_nome_unico",
                violation_error_message="Esse motorista já está cadastrado.",
            ),
        ]

    def __str__(self):
        return self.nome

    @property
    def codigo(self):
        return f"M-{self.pk:03d}" if self.pk else "M-novo"

    @property
    def cpf_mascarado(self):
        return mascarar_cpf(self.cpf)

    @property
    def cnh_final(self):
        return self.cnh[-4:]

    def cnh_valida(self, data=None):
        return self.validade_cnh >= (data or timezone.localdate())

    @property
    def cnh_vence_em_breve(self):
        hoje = timezone.localdate()
        return self.cnh_valida(hoje) and (self.validade_cnh - hoje).days <= 30


class PontoEmbarque(models.Model):
    nome = models.CharField("Nome do ponto", max_length=50)
    endereco = models.CharField("Endereço", max_length=90)
    cep = models.CharField("CEP", max_length=9, blank=True, validators=[validar_cep])
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Ponto de embarque"
        verbose_name_plural = "Pontos de embarque"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                Lower("nome"),
                name="frota_ponto_nome_unico",
                violation_error_message="Esse ponto de embarque já está cadastrado.",
            ),
        ]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.cep = formatar_cep(self.cep)
        super().save(*args, **kwargs)

    @property
    def endereco_completo(self):
        return f"{self.endereco}, CEP {self.cep}" if self.cep else self.endereco


class PedidoPontoEmbarque(models.Model):
    """Atendente pede um local de coleta novo; o administrador aprova ou recusa."""

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        APROVADO = "aprovado", "Aprovado"
        RECUSADO = "recusado", "Recusado"

    nome = models.CharField("Nome do ponto", max_length=50)
    endereco = models.CharField("Endereço", max_length=90)
    cep = models.CharField("CEP", max_length=9, blank=True, validators=[validar_cep])
    justificativa = models.CharField("Por que precisa?", max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    motivo_recusa = models.CharField("Motivo da recusa", max_length=150, blank=True)
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pedidos_ponto"
    )
    respondido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pedido de ponto de embarque"
        verbose_name_plural = "Pedidos de ponto de embarque"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        self.cep = formatar_cep(self.cep)
        super().save(*args, **kwargs)
