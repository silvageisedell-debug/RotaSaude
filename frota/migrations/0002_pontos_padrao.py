from django.db import migrations

from frota.seeds import retirar_pontos, semear_pontos


class Migration(migrations.Migration):
    dependencies = [("frota", "0001_initial")]

    operations = [migrations.RunPython(semear_pontos, retirar_pontos)]
