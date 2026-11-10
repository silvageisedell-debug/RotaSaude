from rest_framework.permissions import BasePermission

from .models import Modulo


class PermissaoModulo(BasePermission):
    """Exige sessão autenticada e o módulo liberado no perfil."""

    modulo = None
    message = "Seu perfil não tem este módulo liberado."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(usuario and usuario.is_authenticated and usuario.pode(self.modulo))


class PermissaoFrota(PermissaoModulo):
    modulo = Modulo.FROTA


class PermissaoSolicitacoes(PermissaoModulo):
    modulo = Modulo.SOLICITACOES


class PermissaoViagens(PermissaoModulo):
    modulo = Modulo.VIAGENS


class PermissaoCaderno(PermissaoModulo):
    modulo = Modulo.CADERNO


class PermissaoInicio(PermissaoModulo):
    modulo = Modulo.INICIO


class PermissaoAdmin(BasePermission):
    message = "Só o administrador lista os usuários."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(usuario and usuario.is_authenticated and usuario.e_admin)
