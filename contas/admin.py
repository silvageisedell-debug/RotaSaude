from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import PermissaoModulo, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("nome", "email", "perfil", "is_active")
    list_filter = ("perfil", "is_active")
    search_fields = ("nome", "email")
    ordering = ("nome",)
    fieldsets = UserAdmin.fieldsets + (("RotaSaúde", {"fields": ("nome", "perfil")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("RotaSaúde", {"fields": ("nome", "email", "perfil")}),)


@admin.register(PermissaoModulo)
class PermissaoModuloAdmin(admin.ModelAdmin):
    list_display = ("perfil", "modulo")
    list_filter = ("perfil",)
