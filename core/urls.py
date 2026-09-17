from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('marketplace/', views.marketplace),
    path('register/', views.register),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('dashboard/', views.dashboard),
    path('planta/<int:pk>/', views.planta_detalhe),
    path('planta/nova/', views.planta_nova),
    path('planta/<int:pk>/editar/', views.planta_editar),
    path('planta/<int:pk>/eliminar/', views.planta_eliminar),
    path('perfil/', views.perfil),
    path('perfil/tipo/', views.perfil_mudar_tipo),
    path('avaliar/<int:vendedor_id>/', views.avaliar_vendedor),
    path('mensagens/', views.mensagens_inbox),
    path('mensagens/<int:outro_id>/', views.mensagens_conversa),
    path('mensagens/<int:outro_id>/enviar/', views.mensagens_enviar),
    path('mensagem/vendedor/<int:vendedor_id>/', views.mensagem_vendedor),
    path('pedidos/gerir/', views.pedidos_gerir),
    path('encomendas/', views.encomendas_cliente),
    path('pedido/criar/<int:planta_id>/', views.pedido_criar),
    path('pedido/<int:pedido_id>/status/', views.pedido_status),
    path('favorito/<int:planta_id>/', views.favorito_toggle),
]
