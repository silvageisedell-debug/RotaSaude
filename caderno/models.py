from django.conf import settings
from django.db import models
from django.utils import timezone


class Anotacao(models.Model):
    """Bilhete do caderno do atendente. Cada um vê só as próprias anotações."""

    CORES = ["#FFFDF6", "#FFF1A8", "#D6F5DE", "#D9E9FF", "#FFDDE4"]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="anotacoes")
    titulo = models.CharField("Título", max_length=60, blank=True)
    texto = models.TextField("Texto", max_length=600, blank=True)
    lembrar_em = models.DateTimeField("Lembrar em", null=True, blank=True)
    cor = models.PositiveSmallIntegerField("Cor", default=0)
    fixada = models.BooleanField("Fixada", default=False)
    concluida = models.BooleanField("Concluída", default=False)
    # Guarda para qual horário o aviso já apareceu, para não repetir o mesmo lembrete.
    avisado_para = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Anotação"
        verbose_name_plural = "Anotações"
        ordering = ["-fixada", models.F("lembrar_em").asc(nulls_last=True), "-criado_em"]

    def __str__(self):
        return self.titulo or self.texto[:40]

    @property
    def cor_hex(self):
        return self.CORES[self.cor % len(self.CORES)]

    @property
    def vencida(self):
        return bool(self.lembrar_em and not self.concluida and self.lembrar_em <= timezone.now())

    @classmethod
    def vencidas_de(cls, usuario):
        return cls.objects.filter(usuario=usuario, concluida=False, lembrar_em__lte=timezone.now())
