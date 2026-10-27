from django import template
from django.utils import timezone
from django.utils.html import format_html

register = template.Library()

# Cores do protótipo para cada situação (por rótulo, como aparecem na tela).
CORES = {
    "Pendente": "#F59E0B", "Aprovada": "#0EA5E9", "Agendada": "#8B5CF6", "Em viagem": "#14B8A6",
    "Concluída": "#16A34A", "Negada": "#E11D48", "Cancelada": "#64748B",
    "Programada": "#8B5CF6", "Em andamento": "#14B8A6",
    "Disponível": "#16A34A", "Programado": "#F59E0B", "Manutenção": "#64748B",
    "Ocupado": "#E11D48", "CNH vencida": "#E11D48",
    "Aprovado": "#16A34A", "Recusado": "#E11D48",
}


@register.filter
def cor(rotulo):
    return CORES.get(str(rotulo), "#64748B")


@register.simple_tag
def pill(rotulo):
    return format_html('<span class="st" style="--c:{}">{}</span>', cor(rotulo), rotulo)


@register.simple_tag
def saudacao(usuario):
    hora = timezone.localtime().hour
    texto = "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"
    return f"{texto}, {usuario.primeiro_nome}"


@register.filter
def livres(situacoes):
    """Quantos itens de uma lista de disponibilidade estão livres."""
    return sum(1 for s in situacoes if s.livre)
