from django import forms
from django.utils import timezone

from .models import Anotacao


class AnotacaoForm(forms.ModelForm):
    class Meta:
        model = Anotacao
        fields = ["titulo", "texto", "lembrar_em", "cor", "fixada"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "nti", "placeholder": "Título (opcional)"}),
            "texto": forms.Textarea(attrs={
                "class": "nta", "rows": 4,
                "placeholder": "Escreva aqui: recado, lembrete, algo para não esquecer...",
            }),
            "lembrar_em": forms.DateTimeInput(attrs={"class": "nin", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "cor": forms.HiddenInput(),
            "fixada": forms.HiddenInput(),
        }

    def clean_cor(self):
        cor = self.cleaned_data.get("cor") or 0
        return cor if 0 <= cor < len(Anotacao.CORES) else 0

    def clean(self):
        dados = super().clean()
        if len((dados.get("texto") or "").strip()) < 2 and not (dados.get("titulo") or "").strip():
            raise forms.ValidationError("Escreva a anotação.")
        lembrar = dados.get("lembrar_em")
        mudou = lembrar != self.instance.lembrar_em
        if lembrar and mudou and lembrar < timezone.now():
            self.add_error("lembrar_em", "Escolha um horário que ainda não passou.")
        return dados
