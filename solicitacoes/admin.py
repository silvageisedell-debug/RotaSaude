from django.contrib import admin

from .models import Categoria, Destino, HistoricoSolicitacao, Solicitacao


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "prioridade")


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ("nome", "cidade", "ativo")
    list_filter = ("ativo", "cidade")


class HistoricoInline(admin.TabularInline):
    model = HistoricoSolicitacao
    extra = 0
    readonly_fields = ("texto", "usuario", "criado_em")
    can_delete = False


@admin.register(Solicitacao)
class SolicitacaoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "paciente", "tipo", "destino", "data", "status")
    list_filter = ("status", "tipo", "categoria")
    search_fields = ("paciente",)
    inlines = [HistoricoInline]
