from django import forms


class EstiloForm:
    """Aplica a classe visual `in` do protótipo. O erro é marcado em templates/parciais/campo.html."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                continue
            css = campo.widget.attrs.get("class", "")
            campo.widget.attrs["class"] = f"{css} in".strip()


def so_digitos(valor):
    return "".join(c for c in str(valor or "") if c.isdigit())


class MotivoForm(EstiloForm, forms.Form):
    """Recusas sempre pedem um motivo, que aparece para quem fez o pedido."""

    motivo = forms.CharField(
        label="Motivo",
        max_length=200,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def clean_motivo(self):
        motivo = " ".join(self.cleaned_data["motivo"].split())
        if len(motivo) < 5:
            raise forms.ValidationError("Escreva o motivo da recusa (mínimo 5 letras).")
        return motivo
