from rest_framework import serializers

from .models import Anotacao


class AnotacaoSerializer(serializers.ModelSerializer):
    cor_hex = serializers.CharField(read_only=True)
    vencida = serializers.BooleanField(read_only=True)

    class Meta:
        model = Anotacao
        fields = [
            "id", "titulo", "texto", "lembrar_em", "cor", "cor_hex", "fixada",
            "concluida", "vencida", "criado_em",
        ]
