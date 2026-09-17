from plantas.models import Mensagem
from usuarios.models import Utilizador
from django.db.models import Q


def notificacoes(request):
    uid = request.session.get('utilizador_id')
    if not uid:
        return {'msgs_nao_lidas': 0, 'utilizador': None, 'pendentes_count': 0}
    try:
        user = Utilizador.objects.get(id=uid)
        count = Mensagem.objects.filter(destinatario=user, lida=False).count()
        from plantas.models import Pedido, ItensPedido
        pedidos_ids = ItensPedido.objects.filter(planta__vendedor=user).values_list('pedido_id', flat=True)
        pendentes = Pedido.objects.filter(id__in=pedidos_ids, status='pendente').count()
        return {
            'msgs_nao_lidas': count,
            'utilizador_global': user,
            'pendentes_count': pendentes,
        }
    except Utilizador.DoesNotExist:
        return {'msgs_nao_lidas': 0, 'utilizador_global': None, 'pendentes_count': 0}
