from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

ADMINISTRADOR = "Administrador"
ATENDENTE = "Atendente"


def papel(usuario):
    if not getattr(usuario, "is_authenticated", False):
        return ""
    if usuario.is_superuser or usuario.groups.filter(name=ADMINISTRADOR).exists():
        return "admin"
    if usuario.groups.filter(name=ATENDENTE).exists():
        return "atendente"
    return ""


def exige(*permitidos):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if papel(request.user) not in permitidos:
                return HttpResponseForbidden("Sem permissão para esta ação.")
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
