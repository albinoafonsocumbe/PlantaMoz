from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import check_password
from .models import Utilizador
from .serializers import RegisterSerializer, UtilizadorSerializer
import secrets

# Simples store de tokens em memória (substituir por JWT em produção)
token_store = {}

def get_utilizador_by_token(request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Token '):
        return None
    token = auth.split(' ')[1]
    uid = token_store.get(token)
    if not uid:
        return None
    try:
        return Utilizador.objects.get(id=uid)
    except Utilizador.DoesNotExist:
        return None


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Utilizador criado', 'id': user.id}, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '')
        senha = request.data.get('senha', '')

        try:
            user = Utilizador.objects.get(email=email)
        except Utilizador.DoesNotExist:
            return Response({'error': 'Credenciais inválidas'}, status=401)

        if not check_password(senha, user.senha):
            return Response({'error': 'Credenciais inválidas'}, status=401)

        token = secrets.token_hex(32)
        token_store[token] = user.id

        return Response({
            'token': token,
            'utilizador': UtilizadorSerializer(user).data
        })


class PerfilView(APIView):
    def get(self, request):
        user = get_utilizador_by_token(request)
        if not user:
            return Response({'error': 'Não autenticado'}, status=401)
        return Response(UtilizadorSerializer(user).data)
