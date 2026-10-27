from django.contrib import admin

from .models import Marca, Modelo, Motorista, PedidoPontoEmbarque, PontoEmbarque, Veiculo


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    search_fields = ("nome",)


@admin.register(Modelo)
class ModeloAdmin(admin.ModelAdmin):
    list_display = ("nome", "marca")
    list_filter = ("marca",)


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "modelo", "tipo", "capacidade", "status")
    list_filter = ("tipo", "status")
    search_fields = ("placa", "chassi")


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria_cnh", "validade_cnh", "ativo")
    list_filter = ("categoria_cnh", "ativo")
    search_fields = ("nome",)


@admin.register(PontoEmbarque)
class PontoEmbarqueAdmin(admin.ModelAdmin):
    list_display = ("nome", "endereco", "cep", "ativo")
    list_filter = ("ativo",)


@admin.register(PedidoPontoEmbarque)
class PedidoPontoEmbarqueAdmin(admin.ModelAdmin):
    list_display = ("nome", "solicitante", "status", "criado_em")
    list_filter = ("status",)
