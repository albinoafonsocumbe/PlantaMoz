from rest_framework import serializers
from .models import Utilizador

class UtilizadorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Utilizador
        fields = ['id', 'nome', 'email', 'telefone', 'localizacao', 'data_criacao']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Utilizador
        fields = ['nome', 'email', 'senha', 'telefone', 'localizacao']
        extra_kwargs = {'senha': {'write_only': True}}

    def create(self, validated_data):
        from django.contrib.auth.hashers import make_password
        validated_data['senha'] = make_password(validated_data['senha'])
        return super().create(validated_data)
