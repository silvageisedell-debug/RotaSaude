from django.forms import ModelForm, NumberInput, TextInput, formset_factory

from .models import Parada


class ParadaForm(ModelForm):
    class Meta:
        model = Parada
        fields = ["local", "ordem"]
        widgets = {
            "local": TextInput(attrs={"maxlength": "120"}),
            "ordem": NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = "form-control"
            if self.is_bound and self.errors.get(name):
                css += " is-invalid"
            field.widget.attrs["class"] = css


ParadaFormSet = formset_factory(ParadaForm, extra=2)
