from django.db import migrations

from contas.seeds import retirar_permissoes, semear_permissoes


class Migration(migrations.Migration):
    dependencies = [("contas", "0001_initial")]

    operations = [migrations.RunPython(semear_permissoes, retirar_permissoes)]
