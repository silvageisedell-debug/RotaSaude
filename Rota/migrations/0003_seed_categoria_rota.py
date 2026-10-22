from django.db import migrations

from Rota.seeds import retirar_seed, semear_categorias


class Migration(migrations.Migration):

    dependencies = [
        ("Rota", "0002_categoriarota"),
    ]

    operations = [
        migrations.RunPython(semear_categorias, retirar_seed),
    ]
