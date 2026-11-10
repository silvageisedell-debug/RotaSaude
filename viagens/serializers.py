from rest_framework import serializers

from solicitacoes.serializers import SolicitacaoSerializer

from .models import Parada, Viagem


class ParadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parada
        fields = ["id", "ordem", "local"]


class ViagemSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(read_only=True)
    veiculo_nome = serializers.StringRelatedField(source="veiculo", read_only=True)
    motorista_nome = serializers.StringRelatedField(source="motorista", read_only=True)
    chegada = serializers.TimeField(read_only=True)

    class Meta:
        model = Viagem
        fields = [
            "id", "codigo", "veiculo", "veiculo_nome", "motorista", "motorista_nome",
            "data", "saida", "chegada", "duracao_horas", "destino", "status",
        ]


class ViagemDetalheSerializer(ViagemSerializer):
    passageiros = SolicitacaoSerializer(many=True, read_only=True)
    paradas = ParadaSerializer(many=True, read_only=True)

    class Meta(ViagemSerializer.Meta):
        fields = ViagemSerializer.Meta.fields + ["passageiros", "paradas"]
