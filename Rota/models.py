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


class CategoriaRota(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome")
    prioridade = models.PositiveIntegerField(verbose_name="Prioridade")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de rota"
        verbose_name_plural = "Categorias de rota"
        ordering = ["prioridade", "nome"]


class Viagem(models.Model):
    disponibilidade = models.ForeignKey(
        Disponibilidade,
        on_delete=models.PROTECT,
        related_name="viagens",
    )
    categoria = models.ForeignKey(
        CategoriaRota,
        on_delete=models.PROTECT,
        related_name="viagens",
    )
    origem = models.CharField(max_length=120, verbose_name="Origem")
    destino = models.CharField(max_length=120, verbose_name="Destino")

    def __str__(self):
        return f"{self.origem} → {self.destino} ({self.categoria})"

    class Meta:
        verbose_name = "Viagem"
        verbose_name_plural = "Viagens"
