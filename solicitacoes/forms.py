from datetime import timedelta

from django import forms
from django.utils import timezone

from frota.models import PontoEmbarque
from portal.forms import EstiloForm

from .models import Destino, Solicitacao


class SolicitacaoForm(EstiloForm, forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = [
            "paciente", "telefone", "tipo", "categoria", "ponto_embarque", "destino",
            "data", "horario", "mobilidade", "acompanhante", "observacoes",
        ]
        widgets = {
            "paciente": forms.TextInput(attrs={"autocomplete": "off"}),
            "telefone": forms.TextInput(attrs={"placeholder": "(17) 90000-0000", "inputmode": "tel", "data-mascara": "telefone"}),
            "data": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "horario": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "observacoes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pontos = PontoEmbarque.objects.filter(ativo=True)
        destinos = Destino.objects.filter(ativo=True)
        if self.instance.pk:
            # Mantém na lista o local já escolhido, mesmo que tenha sido removido depois.
            pontos = pontos | PontoEmbarque.objects.filter(pk=self.instance.ponto_embarque_id)
            destinos = destinos | Destino.objects.filter(pk=self.instance.destino_id)
        self.fields["ponto_embarque"].queryset = pontos.distinct()
        self.fields["destino"].queryset = destinos.distinct()
        self.fields["ponto_embarque"].empty_label = "Selecione o local de embarque"
        self.fields["destino"].empty_label = "Selecione o destino"
        self.fields["categoria"].empty_label = "Selecione a categoria"
        hoje = timezone.localdate()
        self.fields["data"].widget.attrs["min"] = hoje.isoformat()
        if not self.instance.pk and not self.is_bound:
            self.initial.setdefault("data", hoje + timedelta(days=1))
            self.initial.setdefault("horario", "07:00")

    def clean_paciente(self):
        paciente = " ".join(self.cleaned_data["paciente"].split())
        if len(paciente) < 3:
            raise forms.ValidationError("Informe o nome do paciente.")
        return paciente

    def clean_data(self):
        data = self.cleaned_data["data"]
        mudou = not self.instance.pk or data != self.instance.data
        if mudou and data < timezone.localdate():
            raise forms.ValidationError("Escolha uma data a partir de hoje.")
        return data
