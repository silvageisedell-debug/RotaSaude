from django import forms
from django.utils import timezone

from portal.forms import EstiloForm, so_digitos

from .models import Motorista, PedidoPontoEmbarque, PontoEmbarque, Veiculo
from .validadores import formatar_cep, normalizar_placa


class VeiculoForm(EstiloForm, forms.ModelForm):
    # A tela aceita a placa com hífen (8 caracteres); o banco guarda só os 7.
    placa = forms.CharField(label="Placa", max_length=8, widget=forms.TextInput(attrs={"placeholder": "ABC-1D23"}))

    class Meta:
        model = Veiculo
        fields = ["tipo", "modelo", "placa", "chassi", "renavam", "ano", "capacidade"]
        widgets = {
            "chassi": forms.TextInput(attrs={
                "placeholder": "Ex.: 9BD15822A12345678",
                "autocomplete": "off",
                "data-maiusculo": "chassi",
            }),
            "renavam": forms.TextInput(attrs={"placeholder": "11 dígitos (opcional)", "inputmode": "numeric"}),
            "ano": forms.NumberInput(attrs={"placeholder": "2024", "min": 1950}),
            "capacidade": forms.NumberInput(attrs={"min": 1, "max": 60, "placeholder": "Sem contar o motorista"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and not self.is_bound:
            self.initial["placa"] = self.instance.placa_formatada
        self.fields["capacidade"].help_text = "Lugares para pacientes e acompanhantes, sem contar o motorista."

    def clean_placa(self):
        return normalizar_placa(self.cleaned_data["placa"])

    def clean_chassi(self):
        return self.cleaned_data["chassi"].strip().upper()

    def clean_renavam(self):
        renavam = so_digitos(self.cleaned_data.get("renavam"))
        if renavam and len(renavam) != 11:
            raise forms.ValidationError("Renavam inválido. São 11 números.")
        return renavam or None

    def clean_ano(self):
        ano = self.cleaned_data["ano"]
        if ano > timezone.localdate().year + 1:
            raise forms.ValidationError("Ano de fabricação inválido.")
        return ano


class MotoristaForm(EstiloForm, forms.ModelForm):
    cpf = forms.CharField(label="CPF", max_length=14, widget=forms.TextInput(attrs={
        "placeholder": "000.000.000-00", "inputmode": "numeric", "data-mascara": "cpf",
    }))
    cnh = forms.CharField(label="Nº da CNH", max_length=11, widget=forms.TextInput(attrs={
        "placeholder": "11 números", "inputmode": "numeric", "data-mascara": "digitos",
    }))

    class Meta:
        model = Motorista
        fields = ["nome", "cpf", "cnh", "categoria_cnh", "validade_cnh", "telefone", "curso_emergencia"]
        widgets = {
            "nome": forms.TextInput(attrs={"autocomplete": "off"}),
            "validade_cnh": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "telefone": forms.TextInput(attrs={"placeholder": "(17) 90000-0000", "inputmode": "tel", "data-mascara": "telefone"}),
        }

    def clean_nome(self):
        nome = " ".join(self.cleaned_data["nome"].split())
        if len(nome) < 3:
            raise forms.ValidationError("Informe o nome do motorista.")
        return nome

    def clean_cpf(self):
        return so_digitos(self.cleaned_data["cpf"])

    def clean_cnh(self):
        return so_digitos(self.cleaned_data["cnh"])

    def clean_validade_cnh(self):
        validade = self.cleaned_data["validade_cnh"]
        if not self.instance.pk and validade < timezone.localdate():
            raise forms.ValidationError("CNH vencida. Não é possível cadastrar.")
        return validade


class _PontoBase(EstiloForm, forms.ModelForm):
    def clean_nome(self):
        nome = " ".join(self.cleaned_data["nome"].split())
        if len(nome) < 3:
            raise forms.ValidationError("Informe o nome do ponto de embarque.")
        return nome

    def clean_endereco(self):
        endereco = " ".join(self.cleaned_data["endereco"].split())
        if len(endereco) < 5:
            raise forms.ValidationError("Informe o endereço do ponto de embarque (rua, número e bairro).")
        return endereco

    def clean_cep(self):
        return formatar_cep(self.cleaned_data.get("cep"))


_WIDGETS_PONTO = {
    "nome": forms.TextInput(attrs={"placeholder": "Ex.: UBS Vila Nova"}),
    "endereco": forms.TextInput(attrs={"placeholder": "Ex.: Rua das Flores, 120, Centro"}),
    "cep": forms.TextInput(attrs={"placeholder": "00000-000", "inputmode": "numeric", "data-mascara": "cep"}),
}


class PontoEmbarqueForm(_PontoBase):
    class Meta:
        model = PontoEmbarque
        fields = ["nome", "endereco", "cep"]
        widgets = _WIDGETS_PONTO

    def clean_nome(self):
        nome = super().clean_nome()
        if not self.instance.pk:
            # Ponto removido antes volta a valer, em vez de colidir com o nome único.
            removido = PontoEmbarque.objects.filter(nome__iexact=nome, ativo=False).first()
            if removido:
                removido.ativo = True
                self.instance = removido
        return nome


class PedidoPontoForm(_PontoBase):
    class Meta:
        model = PedidoPontoEmbarque
        fields = ["nome", "endereco", "cep", "justificativa"]
        widgets = {
            **_WIDGETS_PONTO,
            "justificativa": forms.TextInput(attrs={"placeholder": "Ex.: vários pacientes da região"}),
        }

    def clean_nome(self):
        nome = super().clean_nome()
        if PontoEmbarque.objects.filter(nome__iexact=nome, ativo=True).exists():
            raise forms.ValidationError("Esse ponto de embarque já está cadastrado.")
        if PedidoPontoEmbarque.objects.filter(nome__iexact=nome, status=PedidoPontoEmbarque.Status.PENDENTE).exists():
            raise forms.ValidationError("Já existe um pedido pendente com esse nome.")
        return nome
