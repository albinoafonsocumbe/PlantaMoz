from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from usuarios.models import Utilizador


def login_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get('utilizador_id')
        if not uid:
            return redirect('/login/')
        try:
            request.utilizador = Utilizador.objects.get(id=uid)
        except Utilizador.DoesNotExist:
            request.session.flush()
            return redirect('/login/')
        return func(request, *args, **kwargs)
    return wrapper


def vendedor_required(func):
    """Apenas vendedores podem aceder. Clientes são redirecionados."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get('utilizador_id')
        if not uid:
            return redirect('/login/')
        try:
            user = Utilizador.objects.get(id=uid)
            request.utilizador = user
        except Utilizador.DoesNotExist:
            return redirect('/login/')
        if not user.is_vendedor:
            messages.error(request, 'Apenas vendedores podem aceder a esta página.')
            return redirect('/dashboard/')
        return func(request, *args, **kwargs)
    return wrapper


def cliente_required(func):
    """Comprar/avaliar está disponível para qualquer conta autenticada (cliente ou vendedor)."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        uid = request.session.get('utilizador_id')
        if not uid:
            return redirect('/login/')
        try:
            user = Utilizador.objects.get(id=uid)
            request.utilizador = user
        except Utilizador.DoesNotExist:
            return redirect('/login/')
        return func(request, *args, **kwargs)
    return wrapper
