from django.contrib import admin

from .models import Parada, Viagem


class ParadaInline(admin.TabularInline):
    model = Parada
    extra = 0


@admin.register(Viagem)
class ViagemAdmin(admin.ModelAdmin):
    list_display = ("codigo", "data", "saida", "veiculo", "motorista", "status")
    list_filter = ("status", "data")
    inlines = [ParadaInline]
