from .acesso import papel


def papel_no_template(request):
    usuario = getattr(request, "user", None)
    return {"papel": papel(usuario) if usuario is not None else ""}
