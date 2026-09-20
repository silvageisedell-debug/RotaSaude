from django.db import models

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
    
    capacidade = models.PositiveIntegerField(
        verbose_name="Capacidade de Passageiros"
    )

    def __str__(self):
        return f"{self.placa} - {self.modelo}"

    class Meta:
        verbose_name_plural = "Veículos"