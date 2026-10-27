from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme


def voltar(request, padrao, *args, **kwargs):
    """Redireciona para o `voltar` do formulário, se for deste site; senão, para a rota padrão."""
    destino = request.POST.get("voltar") or request.GET.get("voltar")
    if destino and url_has_allowed_host_and_scheme(destino, {request.get_host()}, request.is_secure()):
        return redirect(destino)
    return redirect(padrao, *args, **kwargs)
