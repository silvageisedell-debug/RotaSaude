import re

from django.core.exceptions import ValidationError

from portal.forms import so_digitos

PLACA_RE = re.compile(r"^[A-Z]{3}\d[A-Z0-9]\d{2}$")
CHASSI_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


def normalizar_placa(valor):
    return re.sub(r"[^A-Z0-9]", "", str(valor or "").upper())


def validar_placa(valor):
    if not PLACA_RE.match(normalizar_placa(valor)):
        raise ValidationError("Placa inválida. Use o formato ABC-1D23 ou ABC-1234.")


def formatar_placa(valor):
    placa = normalizar_placa(valor)
    return f"{placa[:3]}-{placa[3:]}" if len(placa) == 7 else placa


def validar_chassi(valor):
    if not CHASSI_RE.match(str(valor or "").upper()):
        raise ValidationError("Chassi inválido. São 17 letras e números (as letras I, O e Q não são usadas).")


def cpf_valido(valor):
    cpf = so_digitos(valor)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        if (soma * 10) % 11 % 10 != int(cpf[tamanho]):
            return False
    return True


def validar_cpf(valor):
    if not cpf_valido(valor):
        raise ValidationError("CPF inválido.")


def formatar_cpf(valor):
    cpf = so_digitos(valor)
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf


def mascarar_cpf(valor):
    """Mostra só o miolo do CPF, como pede a LGPD para listas."""
    cpf = so_digitos(valor)
    return f"***.{cpf[3:6]}.{cpf[6:9]}-**" if len(cpf) == 11 else ""


def validar_cnh(valor):
    if len(so_digitos(valor)) != 11:
        raise ValidationError("Número da CNH inválido. São 11 números.")


def validar_cep(valor):
    if valor and len(so_digitos(valor)) != 8:
        raise ValidationError("CEP inválido. Use 8 números, como 15400-000.")


def formatar_cep(valor):
    cep = so_digitos(valor)
    return f"{cep[:5]}-{cep[5:]}" if len(cep) == 8 else cep
