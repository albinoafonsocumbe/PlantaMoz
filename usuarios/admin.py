from django.contrib import admin
from .models import Utilizador


@admin.register(Utilizador)
class UtilizadorAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nome', 'email', 'telefone', 'localizacao', 'data_criacao']
    search_fields = ['nome', 'email']
    ordering      = ['-data_criacao']
    readonly_fields = ['data_criacao']
