CATEGORIAS = (
    ("Urgente", 1),
    ("Prioritária", 2),
    ("Eletiva", 3),
)

DESTINOS = (
    ("Hospital de Amor", "Barretos"),
    ("Hospital de Base", "São José do Rio Preto"),
    ("Santa Casa", "Ribeirão Preto"),
)


def semear_categorias(apps, schema_editor):
    Categoria = apps.get_model("solicitacoes", "Categoria")
    for nome, prioridade in CATEGORIAS:
        Categoria.objects.get_or_create(nome=nome, defaults={"prioridade": prioridade})


def semear_destinos(apps, schema_editor):
    Destino = apps.get_model("solicitacoes", "Destino")
    for nome, cidade in DESTINOS:
        Destino.objects.get_or_create(nome=nome, cidade=cidade)


def semear(apps, schema_editor):
    semear_categorias(apps, schema_editor)
    semear_destinos(apps, schema_editor)


def retirar_seed(apps, schema_editor):
    Categoria = apps.get_model("solicitacoes", "Categoria")
    Destino = apps.get_model("solicitacoes", "Destino")
    Categoria.objects.filter(nome__in=[c[0] for c in CATEGORIAS], solicitacoes=None).delete()
    for nome, cidade in DESTINOS:
        Destino.objects.filter(nome=nome, cidade=cidade, solicitacoes=None).delete()
