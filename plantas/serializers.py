from rest_framework import serializers
from .models import Planta, Pedido, ItensPedido, Avaliacao, Mensagem, Favorito

class PlantaSerializer(serializers.ModelSerializer):
    vendedor_nome = serializers.CharField(source='vendedor.nome', read_only=True)

    class Meta:
        model  = Planta
        fields = ['id', 'nome', 'descricao', 'preco', 'categoria', 'imagem', 'vendedor', 'vendedor_nome', 'data_criacao']
        read_only_fields = ['vendedor', 'data_criacao']


class ItensPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ItensPedido
        fields = ['id', 'planta', 'quantidade', 'preco']


class PedidoSerializer(serializers.ModelSerializer):
    itens = ItensPedidoSerializer(many=True, read_only=True)

    class Meta:
        model  = Pedido
        fields = ['id', 'cliente', 'data_pedido', 'status', 'itens']
        read_only_fields = ['cliente', 'data_pedido']


class AvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Avaliacao
        fields = ['id', 'cliente', 'vendedor', 'nota', 'comentario', 'data_avaliacao']
        read_only_fields = ['cliente', 'data_avaliacao']


class MensagemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Mensagem
        fields = ['id', 'remetente', 'destinatario', 'mensagem', 'data_envio']
        read_only_fields = ['remetente', 'data_envio']


class FavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Favorito
        fields = ['id', 'cliente', 'planta']
        read_only_fields = ['cliente']
