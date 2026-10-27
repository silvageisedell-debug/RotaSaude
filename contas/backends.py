from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """Autentica pelo e-mail (sem diferenciar maiúsculas). O admin também usa este backend."""

    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        login = (email or username or "").strip().lower()
        if not login or password is None:
            return None
        Usuario = get_user_model()
        usuario = (
            Usuario.objects.filter(email__iexact=login).first()
            or Usuario.objects.filter(username__iexact=login).first()
        )
        if usuario is None:
            # Gasta o mesmo tempo de um hash para não revelar se o e-mail existe.
            Usuario().set_password(password)
            return None
        if usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None
