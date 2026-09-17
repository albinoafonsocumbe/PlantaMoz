from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Planta, Pedido, ItensPedido, Avaliacao, Mensagem, Favorito
from .serializers import (PlantaSerializer, PedidoSerializer,
                           AvaliacaoSerializer, MensagemSerializer, FavoritoSerializer)
from usuarios.views import get_utilizador_by_token


def auth_required(request):
    user = get_utilizador_by_token(request)
    if not user:
        return None, Response({'error': 'Não autenticado'}, status=401)
    return user, None


# --- Plantas ---
class PlantaListView(APIView):
    def get(self, request):
        plantas = Planta.objects.all()
        categoria = request.query_params.get('categoria')
        if categoria:
            plantas = plantas.filter(categoria=categoria)
        return Response(PlantaSerializer(plantas, many=True).data)

    def post(self, request):
        user, err = auth_required(request)
        if err: return err
        serializer = PlantaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendedor=user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PlantaDetailView(APIView):
    def get(self, request, pk):
        try:
            planta = Planta.objects.get(pk=pk)
        except Planta.DoesNotExist:
            return Response({'error': 'Não encontrada'}, status=404)
        return Response(PlantaSerializer(planta).data)

    def put(self, request, pk):
        user, err = auth_required(request)
        if err: return err
        try:
            planta = Planta.objects.get(pk=pk, vendedor=user)
        except Planta.DoesNotExist:
            return Response({'error': 'Não encontrada ou sem permissão'}, status=404)
        serializer = PlantaSerializer(planta, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user, err = auth_required(request)
        if err: return err
        try:
            planta = Planta.objects.get(pk=pk, vendedor=user)
        except Planta.DoesNotExist:
            return Response({'error': 'Não encontrada ou sem permissão'}, status=404)
        planta.delete()
        return Response({'message': 'Eliminada'})


# --- Pedidos ---
class PedidoListView(APIView):
    def get(self, request):
        user, err = auth_required(request)
        if err: return err
        pedidos = Pedido.objects.filter(cliente=user)
        return Response(PedidoSerializer(pedidos, many=True).data)

    def post(self, request):
        user, err = auth_required(request)
        if err: return err
        pedido = Pedido.objects.create(cliente=user)
        itens = request.data.get('itens', [])
        for item in itens:
            ItensPedido.objects.create(
                pedido=pedido,
                planta_id=item['planta_id'],
                quantidade=item.get('quantidade', 1),
                preco=item['preco']
            )
        return Response(PedidoSerializer(pedido).data, status=201)


# --- Avaliações ---
class AvaliacaoListView(APIView):
    def get(self, request):
        avaliacoes = Avaliacao.objects.all()
        return Response(AvaliacaoSerializer(avaliacoes, many=True).data)

    def post(self, request):
        user, err = auth_required(request)
        if err: return err
        serializer = AvaliacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cliente=user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# --- Mensagens ---
class MensagemListView(APIView):
    def get(self, request):
        user, err = auth_required(request)
        if err: return err
        mensagens = Mensagem.objects.filter(destinatario=user)
        return Response(MensagemSerializer(mensagens, many=True).data)

    def post(self, request):
        user, err = auth_required(request)
        if err: return err
        serializer = MensagemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(remetente=user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# --- Favoritos ---
class FavoritoListView(APIView):
    def get(self, request):
        user, err = auth_required(request)
        if err: return err
        favoritos = Favorito.objects.filter(cliente=user)
        return Response(FavoritoSerializer(favoritos, many=True).data)

    def post(self, request):
        user, err = auth_required(request)
        if err: return err
        serializer = FavoritoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cliente=user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
