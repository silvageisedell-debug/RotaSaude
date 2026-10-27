from django.conf import settings
from django.db import models


class Categoria(models.Model):
    """Prioridade do atendimento (Urgente, Prioritária, Eletiva). Cadastro no admin e seed."""

    nome = models.CharField("Nome", max_length=50, unique=True)
    prioridade = models.PositiveIntegerField("Prioridade")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["prioridade", "nome"]

    def __str__(self):
        return self.nome


class Destino(models.Model):
    """Hospital ou centro de referência atendido pelas viagens."""

    nome = models.CharField("Unidade", max_length=80)
    cidade = models.CharField("Cidade", max_length=60)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"
        ordering = ["cidade", "nome"]
        constraints = [
            models.UniqueConstraint(fields=["nome", "cidade"], name="solicitacoes_destino_unico"),
        ]

    def __str__(self):
        return f"{self.nome}, {self.cidade}"


class Solicitacao(models.Model):
    class Tipo(models.TextChoices):
        CONSULTA = "consulta", "Consulta"
        HEMODIALISE = "hemodialise", "Hemodiálise"
        EXAME = "exame", "Exame"
        CIRURGIA = "cirurgia", "Cirurgia"
        FISIOTERAPIA = "fisioterapia", "Fisioterapia"

    class Mobilidade(models.TextChoices):
        ANDA = "anda", "Anda sem ajuda"
        CADEIRA = "cadeira", "Cadeira de rodas"
        MACA = "maca", "Maca"

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        APROVADA = "aprovada", "Aprovada"
        AGENDADA = "agendada", "Agendada"
        EM_VIAGEM = "em_viagem", "Em viagem"
        CONCLUIDA = "concluida", "Concluída"
        NEGADA = "negada", "Negada"
        CANCELADA = "cancelada", "Cancelada"

    # Colunas do kanban, na ordem do fluxo.
    FLUXO = [Status.PENDENTE, Status.APROVADA, Status.AGENDADA, Status.EM_VIAGEM, Status.CONCLUIDA, Status.NEGADA]
    EM_ABERTO = [Status.PENDENTE, Status.APROVADA, Status.AGENDADA]

    paciente = models.CharField("Paciente", max_length=60)
    telefone = models.CharField("Telefone", max_length=16, blank=True)
    tipo = models.CharField("Tipo", max_length=20, choices=Tipo.choices, default=Tipo.CONSULTA)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="solicitacoes", verbose_name="Categoria"
    )
    ponto_embarque = models.ForeignKey(
        "frota.PontoEmbarque", on_delete=models.PROTECT, related_name="solicitacoes", verbose_name="Embarque"
    )
    destino = models.ForeignKey(
        Destino, on_delete=models.PROTECT, related_name="solicitacoes", verbose_name="Destino"
    )
    data = models.DateField("Data")
    horario = models.TimeField("Horário")
    acompanhante = models.BooleanField("Com acompanhante", default=False)
    mobilidade = models.CharField("Mobilidade", max_length=10, choices=Mobilidade.choices, default=Mobilidade.ANDA)
    observacoes = models.CharField("Observações", max_length=200, blank=True)

    status = models.CharField("Status", max_length=12, choices=Status.choices, default=Status.PENDENTE)
    motivo_recusa = models.CharField("Motivo da recusa", max_length=200, blank=True)
    viagem = models.ForeignKey(
        "viagens.Viagem", on_delete=models.SET_NULL, null=True, blank=True, related_name="passageiros"
    )
    embarcou = models.BooleanField("Embarcou", default=False)

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="solicitacoes_registradas"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitação"
        verbose_name_plural = "Solicitações"
        ordering = ["data", "horario", "categoria__prioridade"]

    def __str__(self):
        return f"{self.codigo} · {self.paciente}"

    @property
    def codigo(self):
        return f"SOL-{self.pk:03d}" if self.pk else "SOL-nova"

    @property
    def lugares(self):
        """Lugares que ocupa no veículo: o paciente e, se houver, o acompanhante."""
        return 1 + int(self.acompanhante)

    @property
    def em_aberto(self):
        return self.status in self.EM_ABERTO

    def registrar(self, texto, usuario=None):
        return self.historico.create(texto=texto, usuario=usuario)


class HistoricoSolicitacao(models.Model):
    solicitacao = models.ForeignKey(Solicitacao, on_delete=models.CASCADE, related_name="historico")
    texto = models.CharField(max_length=250)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Histórico da solicitação"
        verbose_name_plural = "Históricos das solicitações"
        ordering = ["criado_em", "pk"]

    def __str__(self):
        return self.texto
