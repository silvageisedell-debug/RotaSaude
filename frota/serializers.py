from rest_framework import serializers

from .forms import VeiculoForm
from .models import Modelo, Motorista, PedidoPontoEmbarque, PontoEmbarque, Veiculo


class VeiculoSerializer(serializers.ModelSerializer):
    placa = serializers.CharField(max_length=8)
    modelo_nome = serializers.StringRelatedField(source="modelo", read_only=True)

    class Meta:
        model = Veiculo
        fields = [
            "id", "tipo", "modelo", "modelo_nome", "placa", "chassi",
            "renavam", "ano", "capacidade", "status",
        ]
        read_only_fields = ["id", "modelo_nome", "status"]
        extra_kwargs = {
            "renavam": {"allow_blank": True, "allow_null": True, "required": False},
        }

    def to_representation(self, instance):
        dados = super().to_representation(instance)
        dados["placa"] = instance.placa_formatada
        return dados

    def _campo(self, attrs, nome, padrao=""):
        if nome in attrs:
            valor = attrs[nome]
        elif self.instance is not None:
            valor = self.instance.placa_formatada if nome == "placa" else getattr(self.instance, nome)
        else:
            return padrao
        if hasattr(valor, "pk"):
            return valor.pk
        return "" if valor is None else valor

    def validate(self, attrs):
        formulario = VeiculoForm({
            "tipo": self._campo(attrs, "tipo", Veiculo.Tipo.VAN),
            "modelo": self._campo(attrs, "modelo"),
            "placa": self._campo(attrs, "placa"),
            "chassi": self._campo(attrs, "chassi"),
            "renavam": self._campo(attrs, "renavam"),
            "ano": self._campo(attrs, "ano"),
            "capacidade": self._campo(attrs, "capacidade"),
        }, instance=self.instance)
        if not formulario.is_valid():
            raise serializers.ValidationError(formulario.errors)
        self._formulario = formulario
        return attrs

    def create(self, validated_data):
        return self._formulario.save()

    def update(self, instance, validated_data):
        return self._formulario.save()


class MotoristaSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(read_only=True)
    cpf = serializers.CharField(source="cpf_mascarado", read_only=True)
    cnh_final = serializers.CharField(read_only=True)

    class Meta:
        model = Motorista
        fields = [
            "id", "codigo", "nome", "cpf", "cnh_final", "categoria_cnh",
            "validade_cnh", "telefone", "curso_emergencia", "ativo",
        ]


class PontoEmbarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PontoEmbarque
        fields = ["id", "nome", "endereco", "cep", "ativo"]


class ModeloSerializer(serializers.ModelSerializer):
    marca_nome = serializers.CharField(source="marca.nome", read_only=True)

    class Meta:
        model = Modelo
        fields = ["id", "nome", "marca", "marca_nome"]


class PedidoPontoSerializer(serializers.ModelSerializer):
    solicitante_nome = serializers.CharField(source="solicitante.nome", read_only=True)

    class Meta:
        model = PedidoPontoEmbarque
        fields = [
            "id", "nome", "endereco", "cep", "justificativa", "status",
            "motivo_recusa", "solicitante", "solicitante_nome", "criado_em",
        ]
