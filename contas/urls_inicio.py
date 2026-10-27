from django.urls import reverse

from .models import Modulo

# Página de entrada de cada módulo, na ordem do menu lateral.
URL_DO_MODULO = {
    Modulo.INICIO: "painel:inicio",
    Modulo.SOLICITACOES: "solicitacoes:lista",
    Modulo.VIAGENS: "viagens:quadro",
    Modulo.FROTA: "frota:veiculos",
    Modulo.USUARIOS: "contas:usuarios",
    Modulo.PERMISSOES: "contas:permissoes",
    Modulo.CADERNO: "caderno:inicio",
}


def url_inicial(usuario):
    """Primeira tela liberada para o usuário (o logo e o login levam para ela)."""
    modulos = usuario.modulos()
    if not modulos:
        return reverse("painel:sem_modulo")
    return reverse(URL_DO_MODULO[modulos[0]])
