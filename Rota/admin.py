from django.contrib import admin

from .models import CategoriaRota


@admin.register(CategoriaRota)
class CategoriaRotaAdmin(admin.ModelAdmin):
    list_display = ("nome", "prioridade")
