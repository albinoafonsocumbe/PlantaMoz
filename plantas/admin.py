from django.contrib import admin
from .models import Planta, Pedido, ItensPedido, Avaliacao, Mensagem, Favorito


class ItensPedidoInline(admin.TabularInline):
    model  = ItensPedido
    extra  = 0
    readonly_fields = ['preco']


@admin.register(Planta)
class PlantaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nome', 'categoria', 'preco', 'vendedor', 'data_criacao']
    list_filter   = ['categoria']
    search_fields = ['nome', 'vendedor__nome']
    ordering      = ['-data_criacao']
    readonly_fields = ['data_criacao']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'cliente', 'status', 'data_pedido']
    list_filter   = ['status']
    search_fields = ['cliente__nome']
    ordering      = ['-data_pedido']
    inlines       = [ItensPedidoInline]
    readonly_fields = ['data_pedido']


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'cliente', 'vendedor', 'nota', 'data_avaliacao']
    list_filter   = ['nota']
    ordering      = ['-data_avaliacao']


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display  = ['id', 'remetente', 'destinatario', 'data_envio']
    ordering      = ['-data_envio']


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'cliente', 'planta']
