from django.db import migrations

from solicitacoes.seeds import retirar_seed, semear


class Migration(migrations.Migration):
    dependencies = [("solicitacoes", "0001_initial")]

    operations = [migrations.RunPython(semear, retirar_seed)]
