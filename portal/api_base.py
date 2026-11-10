from rest_framework import serializers, status
from rest_framework.response import Response


def salvar_formulario(formulario_cls, dados, instance=None, **kwargs):
    """Grava pelo formulário que a tela já usa, e devolve os erros em JSON."""
    argumentos = {"data": dados, **kwargs}
    if instance is not None:
        argumentos["instance"] = instance
    formulario = formulario_cls(**argumentos)
    if not formulario.is_valid():
        raise serializers.ValidationError(formulario.errors)
    if hasattr(formulario, "save"):
        return formulario.save()
    return formulario.cleaned_data


def resposta_regra(erro):
    mensagem = erro.args[0] if erro.args else "Não foi possível concluir."
    if not isinstance(mensagem, (list, tuple)):
        mensagem = [str(mensagem)]
    return Response({"detail": list(mensagem)}, status=status.HTTP_400_BAD_REQUEST)
