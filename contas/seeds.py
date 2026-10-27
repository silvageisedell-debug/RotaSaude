# Perfis não administradores começam com Início, Solicitações e Viagens.
PERMISSOES_PADRAO = [
    (perfil, modulo)
    for perfil in ("atendente", "auxadm", "administrativo")
    for modulo in ("inicio", "solicitacoes", "viagens")
]


def semear_permissoes(apps, schema_editor):
    PermissaoModulo = apps.get_model("contas", "PermissaoModulo")
    for perfil, modulo in PERMISSOES_PADRAO:
        PermissaoModulo.objects.get_or_create(perfil=perfil, modulo=modulo)


def retirar_permissoes(apps, schema_editor):
    PermissaoModulo = apps.get_model("contas", "PermissaoModulo")
    for perfil, modulo in PERMISSOES_PADRAO:
        PermissaoModulo.objects.filter(perfil=perfil, modulo=modulo).delete()
