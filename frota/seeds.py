PONTOS = (
    ("UBS Centro", "Rua São João, 500, Centro", "15400-000"),
    ("UBS Jardim Santa Rosa", "Rua das Acácias, 210, Jardim Santa Rosa", ""),
    ("Rodoviária de Olímpia", "Avenida Aurora Forti Neves, 1000, Centro", ""),
    ("Residência do paciente", "Endereço informado pelo paciente", ""),
)


def semear_pontos(apps, schema_editor):
    PontoEmbarque = apps.get_model("frota", "PontoEmbarque")
    for nome, endereco, cep in PONTOS:
        PontoEmbarque.objects.get_or_create(nome=nome, defaults={"endereco": endereco, "cep": cep})


def retirar_pontos(apps, schema_editor):
    PontoEmbarque = apps.get_model("frota", "PontoEmbarque")
    PontoEmbarque.objects.filter(nome__in=[p[0] for p in PONTOS], solicitacoes=None).delete()
