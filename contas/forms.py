from django import forms
from django.contrib.auth import authenticate, password_validation

from portal.forms import EstiloForm

from .models import Perfil, Usuario

MSG_LOGIN = "E-mail ou senha incorretos."
MSG_INATIVO = "Seu acesso ainda não foi liberado ou foi desativado. Fale com o administrador."


class LoginForm(EstiloForm, forms.Form):
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={"placeholder": "seu@email.com", "autofocus": True}))
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput)

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.usuario = None
        super().__init__(*args, **kwargs)

    def clean(self):
        dados = super().clean()
        email, senha = dados.get("email"), dados.get("senha")
        if not email or not senha:
            return dados
        usuario = Usuario.objects.filter(email__iexact=email.strip()).first()
        if usuario and usuario.check_password(senha) and not usuario.is_active:
            raise forms.ValidationError(MSG_INATIVO)
        self.usuario = authenticate(self.request, email=email, password=senha)
        if self.usuario is None:
            raise forms.ValidationError(MSG_LOGIN)
        return dados


class _NovoUsuarioForm(EstiloForm, forms.ModelForm):
    senha = forms.CharField(label="Senha (mínimo 6 caracteres)", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    class Meta:
        model = Usuario
        fields = ["nome", "email"]
        widgets = {
            "nome": forms.TextInput(attrs={"maxlength": 60, "autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"placeholder": "nome@email.com", "autocomplete": "off"}),
        }

    def clean_nome(self):
        nome = " ".join(self.cleaned_data["nome"].split())
        if len(nome) < 3:
            raise forms.ValidationError("Informe o nome completo.")
        if Usuario.objects.filter(nome__iexact=nome).exists():
            raise forms.ValidationError("Já existe um usuário com este nome. Acrescente um sobrenome.")
        return nome

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean_senha(self):
        senha = self.cleaned_data["senha"]
        password_validation.validate_password(senha)
        return senha

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = usuario.email
        usuario.set_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
        return usuario


class SolicitarAcessoForm(_NovoUsuarioForm):
    """Cadastro público de atendente. Nasce sem acesso até o administrador liberar."""

    confirmar = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput)
    lgpd = forms.BooleanField(
        label="Li e aceito o uso dos meus dados pessoais para fins de transporte em saúde, conforme a LGPD.",
        error_messages={"required": "Aceite o termo da LGPD para criar a conta."},
    )

    def clean(self):
        dados = super().clean()
        if dados.get("senha") and dados.get("confirmar") and dados["senha"] != dados["confirmar"]:
            self.add_error("confirmar", "As senhas não conferem.")
        return dados

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.perfil = Perfil.ATENDENTE
        usuario.is_active = False
        if commit:
            usuario.save()
        return usuario


class CadastroUsuarioForm(_NovoUsuarioForm):
    """Cadastro feito pelo administrador. O usuário já entra liberado."""

    perfil = forms.ChoiceField(
        label="Perfil",
        choices=[(p.value, p.label) for p in (Perfil.ATENDENTE, Perfil.AUXADM, Perfil.ADMINISTRATIVO)],
    )

    class Meta(_NovoUsuarioForm.Meta):
        fields = ["nome", "email", "perfil"]

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.is_active = True
        if commit:
            usuario.save()
        return usuario
