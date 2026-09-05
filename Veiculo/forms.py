from django.forms import ModelForm, Select, TextInput, NumberInput
from .models import Veiculo


class VeiculoForm(ModelForm):
    class Meta:
        model = Veiculo
        fields = ["placa", "modelo", "ano", "chassi", "renavam", "capacidade"]
        widgets = {
            "placa": TextInput(attrs={"placeholder": "ABC1D23", "maxlength": "7"}),
            "modelo": Select(),
            "ano": NumberInput(attrs={"placeholder": "2024", "min": "1900"}),
            "chassi": TextInput(attrs={"placeholder": "17 caracteres", "maxlength": "17"}),
            "renavam": TextInput(attrs={"placeholder": "11 dígitos", "maxlength": "11"}),
            "capacidade": NumberInput(attrs={"placeholder": "2 a 5", "min": "2", "max": "5"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = "form-select" if name == "modelo" else "form-control"
            if self.is_bound and self.errors.get(name):
                css += " is-invalid"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css}".strip()
