from django.urls import path
from .views import (PlantaListView, PlantaDetailView, PedidoListView,
                    AvaliacaoListView, MensagemListView, FavoritoListView)

urlpatterns = [
    path('plantas/',          PlantaListView.as_view()),
    path('plantas/<int:pk>/', PlantaDetailView.as_view()),
    path('pedidos/',          PedidoListView.as_view()),
    path('avaliacoes/',       AvaliacaoListView.as_view()),
    path('mensagens/',        MensagemListView.as_view()),
    path('favoritos/',        FavoritoListView.as_view()),
]
