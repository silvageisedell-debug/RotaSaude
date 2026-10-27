from django.db.models import F
from django.urls import reverse

from .models import Modulo
from .urls_inicio import URL_DO_MODULO, url_inicial

ICONES = {
    Modulo.INICIO: '<path d="M3 11l9-8 9 8v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    Modulo.SOLICITACOES: '<rect x="6" y="4" width="12" height="17" rx="2"/><path d="M9 4h6v3H9zM9 12h6M9 16h4"/>',
    Modulo.VIAGENS: '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6"/>',
    Modulo.FROTA: '<path d="M2 16V7h11v9M13 10h4l4 4v2h-2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/>',
    Modulo.USUARIOS: '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3 3-5 6-5s6 2 6 5M16 5a3 3 0 0 1 0 6M21 19c0-2-1-3.5-3-4.3"/>',
    Modulo.PERMISSOES: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    Modulo.CADERNO: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 3v18M12 8h4M12 12h4"/>',
}


def menu(request):
    """Monta o menu lateral, os selos de pendência e a faixa de viagens."""
    usuario = getattr(request, "user", None)
    if not usuario or not usuario.is_authenticated:
        return {}

    # Imports locais: os apps de domínio dependem de contas, não o contrário.
    from caderno.models import Anotacao
    from frota.models import PedidoPontoEmbarque
    from solicitacoes.models import Solicitacao
    from viagens.models import Viagem

    modulos = usuario.modulos()
    selos = {}
    if Modulo.SOLICITACOES in modulos:
        selos[Modulo.SOLICITACOES] = Solicitacao.objects.filter(status=Solicitacao.Status.PENDENTE).count()
    if usuario.e_admin:
        selos[Modulo.FROTA] = PedidoPontoEmbarque.objects.filter(status=PedidoPontoEmbarque.Status.PENDENTE).count()
    lembretes = []
    if Modulo.CADERNO in modulos:
        vencidas = Anotacao.vencidas_de(usuario)
        selos[Modulo.CADERNO] = vencidas.count()
        lembretes = list(vencidas.exclude(avisado_para=F("lembrar_em"))[:5])

    abas = []
    for m in modulos:
        nome_url = URL_DO_MODULO[m]
        abas.append({
            "modulo": m,
            "titulo": Modulo(m).label,
            "url": reverse(nome_url),
            "icone": ICONES[m],
            "selo": selos.get(m, 0),
            "ativa": _aba_ativa(m, request),
        })

    em_andamento = Viagem.objects.filter(status=Viagem.Status.EM_ANDAMENTO).count()
    return {
        "menu_abas": abas,
        "url_inicio": url_inicial(usuario),
        "viagens_em_andamento": em_andamento,
        "lembretes_pendentes": lembretes,
        "user_pode_viagens": Modulo.VIAGENS in modulos,
    }


def _aba_ativa(modulo, request):
    match = request.resolver_match
    if not match:
        return False
    if modulo == Modulo.USUARIOS:
        return match.namespace == "contas" and match.url_name in ("usuarios", "alternar_acesso")
    if modulo == Modulo.PERMISSOES:
        return match.namespace == "contas" and match.url_name == "permissoes"
    namespace = {Modulo.INICIO: "painel", Modulo.CADERNO: "caderno"}.get(modulo, modulo)
    return match.namespace == namespace
