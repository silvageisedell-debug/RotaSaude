from datetime import time

from django import forms
from django.db.models import Q
from django.utils import timezone

from frota.models import Motorista, Veiculo
from portal.forms import EstiloForm
from solicitacoes.models import Solicitacao

from .models import HORA_FIM, HORA_INICIO
from .services import validar_programacao

# Saídas de meia em meia hora dentro da janela de operação.
HORARIOS_SAIDA = [
    (f"{h:02d}:{m:02d}", f"{h:02d}:{m:02d}")
    for h in range(HORA_INICIO, HORA_FIM)
    for m in (0, 30)
]


class ProgramarViagemForm(EstiloForm, forms.Form):
    data = forms.DateField(label="Data", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    saida = forms.ChoiceField(label="Saída", choices=HORARIOS_SAIDA, initial="07:00")
    duracao_horas = forms.IntegerField(label="Duração (horas)", min_value=1, max_value=12, initial=6)
    veiculo = forms.ModelChoiceField(label="Veículo", queryset=Veiculo.objects.none(), empty_label="Selecione o veículo")
    motorista = forms.ModelChoiceField(label="Motorista", queryset=Motorista.objects.none(), empty_label="Selecione o motorista")
    solicitacoes = forms.ModelMultipleChoiceField(
        label="Pacientes",
        queryset=Solicitacao.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": "Marque ao menos um paciente."},
    )

    def __init__(self, *args, preselecionada=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["veiculo"].queryset = Veiculo.objects.select_related("modelo__marca")
        self.fields["motorista"].queryset = Motorista.objects.filter(ativo=True)
        aguardando = Q(status=Solicitacao.Status.APROVADA)
        if preselecionada:
            aguardando |= Q(pk=preselecionada.pk, status=Solicitacao.Status.PENDENTE)
        self.fields["solicitacoes"].queryset = (
            Solicitacao.objects.filter(aguardando).select_related("destino", "ponto_embarque").order_by("data", "horario")
        )
        if not self.is_bound:
            self.initial.setdefault("data", preselecionada.data if preselecionada else timezone.localdate())
            if preselecionada:
                self.initial["solicitacoes"] = [preselecionada.pk]

    def clean_saida(self):
        hora, minuto = (int(p) for p in self.cleaned_data["saida"].split(":"))
        return time(hora, minuto)

    def clean(self):
        dados = super().clean()
        campos = ("data", "saida", "duracao_horas", "veiculo", "motorista", "solicitacoes")
        if all(dados.get(c) for c in campos):
            for erro in validar_programacao(
                dados["data"], dados["saida"], dados["duracao_horas"],
                dados["veiculo"], dados["motorista"], list(dados["solicitacoes"]),
            ):
                self.add_error(None, erro)
        return dados
