from django.db import migrations


def semear_perfis(apps, schema_editor):
    from django.contrib.auth.hashers import make_password

    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")
    administradores, _ = Group.objects.get_or_create(name="Administrador")
    atendentes, _ = Group.objects.get_or_create(name="Atendente")

    def garante(username, senha, primeiro_nome, grupo, superuser=False):
        usuario, criado = User.objects.get_or_create(
            username=username,
            defaults={
                "email": username,
                "first_name": primeiro_nome,
                "is_staff": superuser,
                "is_superuser": superuser,
            },
        )
        if criado:
            usuario.password = make_password(senha)
            usuario.save(update_fields=["password"])
        usuario.groups.add(grupo)

    garante("admin@rotasaude.com.br", "admin123", "Carla", administradores, True)
    garante("atendente@rotasaude.com.br", "atend123", "Rafael", atendentes)


class Migration(migrations.Migration):

    dependencies = [
        ("Rota", "0005_parada"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(semear_perfis, migrations.RunPython.noop),
    ]
