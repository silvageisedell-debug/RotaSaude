from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def modulo_requerido(modulo):
    """Exige login e que o perfil do usuário tenha o módulo liberado."""

    def decorador(view):
        @login_required
        @wraps(view)
        def envolvida(request, *args, **kwargs):
            if not request.user.pode(modulo):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return envolvida

    return decorador


def so_admin(view):
    @login_required
    @wraps(view)
    def envolvida(request, *args, **kwargs):
        if not request.user.e_admin:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return envolvida
