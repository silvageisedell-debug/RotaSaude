from rest_framework import serializers

from .models import Categoria, Destino, HistoricoSolicitacao, Solicitacao


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nome", "prioridade"]


class DestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destino
        fields = ["id", "nome", "cidade", "ativo"]


class HistoricoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.SerializerMethodField()

    def get_usuario_nome(self, historico):
        return historico.usuario.nome if historico.usuario_id else None

    class Meta:
        model = HistoricoSolicitacao
        fields = ["id", "texto", "usuario_nome", "criado_em"]


class SolicitacaoSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(read_only=True)
    destino_nome = serializers.StringRelatedField(source="destino", read_only=True)
    ponto_nome = serializers.StringRelatedField(source="ponto_embarque", read_only=True)
    categoria_nome = serializers.StringRelatedField(source="categoria", read_only=True)

    class Meta:
        model = Solicitacao
        fields = [
            "id", "codigo", "paciente", "telefone", "tipo", "categoria", "categoria_nome",
            "ponto_embarque", "ponto_nome", "destino", "destino_nome", "data", "horario",
            "mobilidade", "acompanhante", "observacoes", "status", "motivo_recusa",
            "viagem", "embarcou",
        ]


class SolicitacaoDetalheSerializer(SolicitacaoSerializer):
    historico = HistoricoSerializer(many=True, read_only=True)

    class Meta(SolicitacaoSerializer.Meta):
        fields = SolicitacaoSerializer.Meta.fields + ["historico"]
