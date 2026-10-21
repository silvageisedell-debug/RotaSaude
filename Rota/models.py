from django.db import models

from Veiculo.models import Veiculo


class Disponibilidade(models.Model):
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.PROTECT,
        related_name="disponibilidades",
    )
    data = models.DateField(verbose_name="Data")
    horario = models.TimeField(verbose_name="Horário")
    vagas = models.PositiveIntegerField(verbose_name="Vagas")

    def __str__(self):
        return (
            f"{self.veiculo.placa} — "
            f"{self.data.strftime('%d/%m/%Y')} "
            f"{self.horario.strftime('%H:%M')}"
        )

    class Meta:
        verbose_name = "Disponibilidade"
        verbose_name_plural = "Disponibilidades"
