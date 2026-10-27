from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .demo import CONTAS_DEMO
from .forms import CadastroUsuarioForm, LoginForm, SolicitarAcessoForm
from .models import (
    MODULOS_CONFIGURAVEIS,
    PERFIS_CONFIGURAVEIS,
    Modulo,
    PermissaoModulo,
    Usuario,
)
from .permissoes import so_admin
from .urls_inicio import url_inicial


def entrar(request):
    if request.user.is_authenticated:
        return redirect(url_inicial(request.user))
    form = LoginForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        login(request, form.usuario)
        destino = request.POST.get("next") or request.GET.get("next")
        if destino and url_has_allowed_host_and_scheme(destino, {request.get_host()}, request.is_secure()):
            return redirect(destino)
        return redirect(url_inicial(form.usuario))
    contas_teste = []
    if settings.DEBUG:
        existentes = set(Usuario.objects.filter(is_active=True).values_list("email", flat=True))
        contas_teste = [c for c in CONTAS_DEMO if c["email"] in existentes]
    return render(request, "contas/login.html", {
        "form": form,
        "contas_teste": contas_teste,
        "next": request.GET.get("next", ""),
    })


@require_POST
def sair(request):
    logout(request)
    return redirect("contas:login")


def solicitar_acesso(request):
    form = SolicitarAcessoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cadastro enviado. O administrador precisa liberar seu acesso antes do primeiro login.")
        return redirect("contas:login")
    return render(request, "contas/solicitar_acesso.html", {"form": form})


@so_admin
def usuarios(request):
    form = CadastroUsuarioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        messages.success(request, f"{usuario.primeiro_nome} cadastrado(a) e com acesso liberado.")
        return redirect("contas:usuarios")
    lista = Usuario.objects.order_by("is_active", "nome")
    return render(request, "contas/usuarios.html", {"form": form, "usuarios": lista, "abrir_form": form.is_bound})


@so_admin
@require_POST
def alternar_acesso(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario.e_admin:
        messages.error(request, "O acesso do administrador fica sempre ativo.")
        return redirect("contas:usuarios")
    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=["is_active"])
    messages.success(request, f"{usuario.nome}: {'ativado' if usuario.is_active else 'desativado'}.")
    return redirect("contas:usuarios")


@so_admin
def permissoes(request):
    if request.method == "POST":
        perfil = request.POST.get("perfil")
        modulo = request.POST.get("modulo")
        if perfil in PERFIS_CONFIGURAVEIS and modulo in MODULOS_CONFIGURAVEIS:
            liberar = request.POST.get("liberado") == "1"
            if liberar:
                PermissaoModulo.objects.get_or_create(perfil=perfil, modulo=modulo)
            else:
                PermissaoModulo.objects.filter(perfil=perfil, modulo=modulo).delete()
            messages.success(
                request,
                f"{dict(Usuario._meta.get_field('perfil').choices)[perfil]}: "
                f"{'liberado' if liberar else 'bloqueado'} em {Modulo(modulo).label}.",
            )
        return redirect("contas:permissoes")

    ligados = set(PermissaoModulo.objects.values_list("perfil", "modulo"))
    linhas = []
    for modulo in Modulo:
        if modulo == Modulo.CADERNO:
            continue
        configuravel = modulo in MODULOS_CONFIGURAVEIS
        linhas.append({
            "modulo": modulo,
            "configuravel": configuravel,
            "celulas": [
                {"perfil": p, "ligado": configuravel and (p.value, modulo.value) in ligados}
                for p in PERFIS_CONFIGURAVEIS
            ],
        })
    return render(request, "contas/permissoes.html", {"linhas": linhas, "perfis": PERFIS_CONFIGURAVEIS})
