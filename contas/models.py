from django.contrib.auth.models import AbstractUser
from django.db import models


class Perfil(models.TextChoices):
    ADMIN = "admin", "Administrador"
    ATENDENTE = "atendente", "Atendente / Regulador"
    AUXADM = "auxadm", "Auxiliar administrativo"
    ADMINISTRATIVO = "administrativo", "Administrativo"


class Modulo(models.TextChoices):
    INICIO = "inicio", "Início"
    SOLICITACOES = "solicitacoes", "Solicitações"
    VIAGENS = "viagens", "Viagens"
    FROTA = "frota", "Frota"
    USUARIOS = "usuarios", "Usuários"
    PERMISSOES = "permissoes", "Permissões"
    CADERNO = "caderno", "Caderno"


# O administrador enxerga tudo, menos o caderno (que é pessoal do atendente).
MODULOS_ADMIN = [
    Modulo.INICIO,
    Modulo.SOLICITACOES,
    Modulo.VIAGENS,
    Modulo.FROTA,
    Modulo.USUARIOS,
    Modulo.PERMISSOES,
]
# Usuários e Permissões nunca são liberados para outros perfis.
MODULOS_SO_ADMIN = [Modulo.USUARIOS, Modulo.PERMISSOES]
# Módulos que a matriz deixa ligar e desligar para os perfis não administradores.
MODULOS_CONFIGURAVEIS = [Modulo.INICIO, Modulo.SOLICITACOES, Modulo.VIAGENS, Modulo.FROTA]
PERFIS_CONFIGURAVEIS = [Perfil.ATENDENTE, Perfil.AUXADM, Perfil.ADMINISTRATIVO]


class Usuario(AbstractUser):
    """Usuário do sistema. Entra com e-mail e senha; `is_active` é o acesso liberado."""

    nome = models.CharField("Nome completo", max_length=60)
    email = models.EmailField("E-mail", unique=True)
    perfil = models.CharField(
        "Perfil", max_length=20, choices=Perfil.choices, default=Perfil.ATENDENTE
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["nome"]

    def __str__(self):
        return self.nome or self.email

    def save(self, *args, **kwargs):
        self.email = (self.email or "").strip().lower()
        if not self.username:
            self.username = self.email
        if self.is_superuser:
            self.perfil = Perfil.ADMIN
        if not self.nome:
            self.nome = self.get_full_name() or self.username
        super().save(*args, **kwargs)

    @property
    def e_admin(self):
        return self.perfil == Perfil.ADMIN

    @property
    def primeiro_nome(self):
        return self.nome.split(" ")[0] if self.nome else ""

    def pode(self, modulo):
        if not self.is_authenticated or not self.is_active:
            return False
        if self.e_admin:
            return modulo in MODULOS_ADMIN
        if modulo == Modulo.CADERNO:
            return self.perfil == Perfil.ATENDENTE
        if modulo in MODULOS_SO_ADMIN:
            return False
        return PermissaoModulo.objects.filter(perfil=self.perfil, modulo=modulo).exists()

    def modulos(self):
        """Módulos liberados, na ordem do menu."""
        if self.e_admin:
            return list(MODULOS_ADMIN)
        liberados = set(
            PermissaoModulo.objects.filter(perfil=self.perfil).values_list("modulo", flat=True)
        )
        if self.perfil == Perfil.ATENDENTE:
            liberados.add(Modulo.CADERNO)
        return [m for m in Modulo.values if m in liberados and m not in MODULOS_SO_ADMIN]


class PermissaoModulo(models.Model):
    """Uma linha liga um módulo a um perfil. Sem linha, o módulo fica oculto."""

    perfil = models.CharField(max_length=20, choices=Perfil.choices)
    modulo = models.CharField(max_length=20, choices=Modulo.choices)

    class Meta:
        verbose_name = "Permissão de módulo"
        verbose_name_plural = "Permissões de módulo"
        constraints = [
            models.UniqueConstraint(fields=["perfil", "modulo"], name="contas_permissao_unica"),
        ]

    def __str__(self):
        return f"{self.get_perfil_display()} → {self.get_modulo_display()}"
