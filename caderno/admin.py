from django.contrib import admin

from .models import Anotacao


@admin.register(Anotacao)
class AnotacaoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "usuario", "lembrar_em", "concluida")
    list_filter = ("concluida",)
