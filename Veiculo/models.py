from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Marca(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome da Marca")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Marcas"

class Modelo(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome do Modelo")
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name="modelos")

    def __str__(self):
        return f"{self.marca.nome} {self.nome}"

    class Meta:
        verbose_name_plural = "Modelos"

class Veiculo(models.Model):
    placa = models.CharField(max_length=7, unique=True, verbose_name="Placa")
    modelo = models.ForeignKey(Modelo, on_delete=models.PROTECT, related_name="veiculos")
    ano = models.PositiveIntegerField(verbose_name="Ano de Fabricação")
    chassi = models.CharField(max_length=17, unique=True, verbose_name="Chassi")
    renavam = models.CharField(max_length=11, unique=True, verbose_name="Renavam")
    
    # Regra de negócio: capacidade entre 2 e 5.
    # Usamos validators para garantir isso no nível de formulário/admin.
    capacidade = models.PositiveIntegerField(
        validators=[
            MinValueValidator(2, message="A capacidade mínima é de 2 pessoas."),
            MaxValueValidator(5, message="A capacidade máxima é de 5 pessoas.")
        ],
        help_text="Deve estar entre 2 e 5 ocupantes."
    )

    def clean(self):
        """Validação adicional no nível do banco de dados/save()"""
        if self.capacidade < 2 or self.capacidade > 5:
            raise ValidationError({'capacidade': "Capacidade deve ser entre 2 e 5 pessoas."})

    def __str__(self):
        return f"{self.placa} - {self.modelo}"

    class Meta:
        verbose_name_plural = "Veículos"