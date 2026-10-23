CATEGORIAS = (
    ("Urgente", 1),
    ("Prioritária", 2),
    ("Eletiva", 3),
)


def semear_categorias(apps, schema_editor):
    CategoriaRota = apps.get_model("Rota", "CategoriaRota")
    for nome, prioridade in CATEGORIAS:
        CategoriaRota.objects.get_or_create(
            nome=nome,
            defaults={"prioridade": prioridade},
        )


def retirar_seed(apps, schema_editor):
    CategoriaRota = apps.get_model("Rota", "CategoriaRota")
    nomes = [nome for nome, _prioridade in CATEGORIAS]
    CategoriaRota.objects.filter(nome__in=nomes).delete()
