from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Janela de operação do quadro de horários: das 05:00 às 20:00.
HORA_INICIO = 5
HORA_FIM = 20


class Viagem(models.Model):
    class Status(models.TextChoices):
        PROGRAMADA = "programada", "Programada"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        CONCLUIDA = "concluida", "Concluída"
        CANCELADA = "cancelada", "Cancelada"

    ATIVAS = [Status.PROGRAMADA, Status.EM_ANDAMENTO]

    veiculo = models.ForeignKey("frota.Veiculo", on_delete=models.PROTECT, related_name="viagens")
    motorista = models.ForeignKey("frota.Motorista", on_delete=models.PROTECT, related_name="viagens")
    data = models.DateField("Data")
    saida = models.TimeField("Saída")
    duracao_horas = models.PositiveSmallIntegerField(
        "Duração (horas)", validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    destino = models.CharField("Destino", max_length=250)
    status = models.CharField("Status", max_length=15, choices=Status.choices, default=Status.PROGRAMADA)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Viagem"
        verbose_name_plural = "Viagens"
        ordering = ["data", "saida"]

    def __str__(self):
        return f"{self.codigo} · {self.destino}"

    @property
    def codigo(self):
        return f"VG-{self.pk:02d}" if self.pk else "VG-nova"

    @property
    def chegada(self):
        fim = datetime.combine(self.data, self.saida) + timedelta(hours=self.duracao_horas)
        return fim.time() if fim.date() == self.data else time(23, 59)

    @property
    def inicio_minutos(self):
        return self.saida.hour * 60 + self.saida.minute

    @property
    def fim_minutos(self):
        return self.inicio_minutos + self.duracao_horas * 60

    @property
    def gantt_esquerda(self):
        """Posição da barra no quadro de horários, em % da janela de 05h às 20h."""
        janela = (HORA_FIM - HORA_INICIO) * 60
        return round(max(0, self.inicio_minutos - HORA_INICIO * 60) / janela * 100, 2)

    @property
    def gantt_largura(self):
        janela = (HORA_FIM - HORA_INICIO) * 60
        return round(min(self.duracao_horas * 60, janela) / janela * 100, 2)

    @property
    def ativa(self):
        return self.status in self.ATIVAS


class Parada(models.Model):
    """Itinerário da viagem: locais na ordem em que o veículo passa."""

    viagem = models.ForeignKey(Viagem, on_delete=models.CASCADE, related_name="paradas")
    ordem = models.PositiveIntegerField("Ordem")
    local = models.CharField("Local", max_length=120)

    class Meta:
        verbose_name = "Parada"
        verbose_name_plural = "Paradas"
        ordering = ["ordem"]
        constraints = [
            models.UniqueConstraint(fields=["viagem", "ordem"], name="viagens_parada_ordem_unica"),
        ]

    def __str__(self):
        return f"{self.ordem}. {self.local}"
