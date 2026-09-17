from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from plantas.models import Planta, Pedido, Favorito, Avaliacao, ItensPedido, Mensagem
from usuarios.models import Utilizador


EMOJI_CATEGORIA = {
    'ornamental': '🌸',
    'medicinal': '🌿',
    'fruteira': '🍋',
    'aromatica': '🌺',
}

def get_emoji(categoria):
    return EMOJI_CATEGORIA.get(categoria, '🪴')

def get_utilizador(request):
    uid = request.session.get('utilizador_id')
    if not uid:
        return None
    try:
        return Utilizador.objects.get(id=uid)
    except Utilizador.DoesNotExist:
        return None


def marketplace(request):
    from django.core.paginator import Paginator
    plantas = Planta.objects.select_related('vendedor').all()
    categoria = request.GET.get('categoria', '')
    search = request.GET.get('q', '')
    preco_max = request.GET.get('preco_max', '')
    ordem = request.GET.get('ordem', '')

    if categoria:
        plantas = plantas.filter(categoria=categoria)
    if search:
        plantas = plantas.filter(nome__icontains=search)
    if preco_max:
        plantas = plantas.filter(preco__lte=preco_max)
    if ordem == 'preco_asc':
        plantas = plantas.order_by('preco')
    elif ordem == 'preco_desc':
        plantas = plantas.order_by('-preco')
    else:
        plantas = plantas.order_by('-data_criacao')

    paginator = Paginator(plantas, 12)
    page = request.GET.get('page', 1)
    plantas_page = paginator.get_page(page)

    categorias = [
        ('ornamental', 'fa-spa', 'Ornamental', 'Flores e plantas decorativas'),
        ('medicinal', 'fa-mortar-pestle', 'Medicinal', 'Plantas com propriedades curativas'),
        ('fruteira', 'fa-apple-whole', 'Fruteira', 'Árvores e plantas de fruto'),
        ('aromatica', 'fa-wind', 'Aromática', 'Ervas e plantas perfumadas'),
    ]
    return render(request, 'marketplace.html', {
        'plantas': plantas_page,
        'categorias': categorias,
        'categoria': categoria,
        'search': search,
        'preco_max': preco_max,
        'ordem': ordem,
        'total': paginator.count,
        'utilizador': get_utilizador(request),
    })


def index(request):
    plantas = Planta.objects.select_related('vendedor').all()[:8]
    categorias = [
        ('ornamental', 'fa-spa', 'Ornamental', 'Flores e plantas decorativas'),
        ('medicinal', 'fa-mortar-pestle', 'Medicinal', 'Plantas com propriedades curativas'),
        ('fruteira', 'fa-apple-whole', 'Fruteira', 'Árvores e plantas de fruto'),
        ('aromatica', 'fa-wind', 'Aromática', 'Ervas e plantas perfumadas'),
    ]
    steps = [
        {'icon': 'fa-user-plus', 'title': 'Regista-te', 'desc': 'Cria a tua conta como cliente ou vendedor.'},
        {'icon': 'fa-store', 'title': 'Explora', 'desc': 'Navega pelo marketplace e descobre plantas.'},
        {'icon': 'fa-cart-shopping', 'title': 'Encomenda', 'desc': 'Faz o pedido directamente ao vendedor.'},
        {'icon': 'fa-truck', 'title': 'Recebe', 'desc': 'A planta é entregue na tua localização.'},
    ]
    stats = [
        (Planta.objects.count(), 'Plantas à venda', 'fa-leaf'),
        (Utilizador.objects.count(), 'Membros activos', 'fa-store'),
        (Pedido.objects.count(), 'Pedidos realizados', 'fa-shopping-bag'),
        ('10+', 'Províncias cobertas', 'fa-map-marker-alt'),
    ]
    return render(request, 'index.html', {
        'plantas': plantas,
        'categorias': categorias,
        'steps': steps,
        'stats': stats,
    })


def register(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '')
        confirmar = request.POST.get('confirmar_senha', '')

        if len(nome) < 3:
            return render(request, 'register.html', {'erro': 'O nome de utilizador deve ter pelo menos 3 caracteres.'})
        if Utilizador.objects.filter(nome__iexact=nome).exists():
            return render(request, 'register.html', {'erro': 'Este nome de utilizador já está em uso.'})
        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            return render(request, 'register.html', {'erro': 'Indica um email válido.'})
        if Utilizador.objects.filter(email__iexact=email).exists():
            return render(request, 'register.html', {'erro': 'Este email já está registado.'})
        if len(senha) < 6:
            return render(request, 'register.html', {'erro': 'A senha deve ter pelo menos 6 caracteres.'})
        if senha != confirmar:
            return render(request, 'register.html', {'erro': 'As senhas não coincidem.'})

        Utilizador.objects.create(
            nome=nome,
            email=email,
            senha=make_password(senha),
            tipo='cliente',
        )
        messages.success(request, 'Conta criada com sucesso! Já podes entrar.')
        return redirect('/login/')
    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        identificador = request.POST.get('identificador', '').strip()
        senha = request.POST.get('senha', '')
        user = None
        if identificador:
            user = Utilizador.objects.filter(email__iexact=identificador).first()
            if user is None:
                user = Utilizador.objects.filter(nome__iexact=identificador).first()
        if user is None:
            return render(request, 'login.html', {'erro': 'Utilizador não encontrado.'})
        if not check_password(senha, user.senha):
            return render(request, 'login.html', {'erro': 'Senha incorrecta.'})
        request.session['utilizador_id'] = user.id
        request.session['utilizador_nome'] = user.nome
        if request.POST.get('lembrar'):
            request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            request.session.set_expiry(0)
        return redirect('/dashboard/')
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('/')


def dashboard(request):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')

    if user.is_vendedor:
        plantas = Planta.objects.filter(vendedor=user)
        pedidos_ids = ItensPedido.objects.filter(planta__vendedor=user).values_list('pedido_id', flat=True)
        pedidos_vendedor = Pedido.objects.filter(id__in=pedidos_ids)
        pendentes_count = pedidos_vendedor.filter(status='pendente').count()
        avaliacoes = Avaliacao.objects.filter(vendedor=user)
        media = round(sum(a.nota for a in avaliacoes) / avaliacoes.count(), 1) if avaliacoes.exists() else None
        return render(request, 'dashboard.html', {
            'utilizador':      user,
            'plantas':         plantas,
            'total_plantas':   plantas.count(),
            'pendentes_count': pendentes_count,
            'media_avaliacao': media,
            'is_vendedor':     True,
        })
    else:
        pedidos_cliente = Pedido.objects.filter(cliente=user)
        favoritos = Favorito.objects.filter(cliente=user)
        return render(request, 'dashboard.html', {
            'utilizador':      user,
            'pedidos':         pedidos_cliente,
            'total_pedidos':   pedidos_cliente.count(),
            'total_favoritos': favoritos.count(),
            'is_vendedor':     False,
        })


def planta_detalhe(request, pk):
    planta = get_object_or_404(Planta, pk=pk)
    avaliacoes = Avaliacao.objects.filter(vendedor=planta.vendedor).select_related('cliente')
    return render(request, 'planta_detalhe.html', {
        'planta': planta,
        'avaliacoes': avaliacoes,
        'utilizador': get_utilizador(request),
    })


def planta_nova(request):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')
    if not user.is_vendedor:
        messages.error(request, 'Apenas vendedores podem publicar plantas.')
        return redirect('/dashboard/')
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        preco_raw = request.POST.get('preco', '0')
        try:
            preco = float(preco_raw)
            if preco <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Preço inválido. Deve ser um valor positivo.')
            return render(request, 'planta_form.html')
        Planta.objects.create(
            nome=nome,
            descricao=request.POST.get('descricao', ''),
            preco=preco,
            categoria=request.POST.get('categoria', ''),
            imagem=request.FILES.get('imagem'),
            vendedor=user
        )
        messages.success(request, 'Planta publicada com sucesso!')
        return redirect('/dashboard/')
    return render(request, 'planta_form.html')


def planta_editar(request, pk):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')
    planta = get_object_or_404(Planta, pk=pk, vendedor=user)
    if request.method == 'POST':
        preco_raw = request.POST.get('preco', '0')
        try:
            preco = float(preco_raw)
            if preco <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Preço inválido. Deve ser um valor positivo.')
            return render(request, 'planta_form.html', {'planta': planta})
        planta.nome = request.POST['nome']
        planta.descricao = request.POST.get('descricao', '')
        planta.preco = preco
        planta.categoria = request.POST.get('categoria', '')
        if request.FILES.get('imagem'):
            planta.imagem = request.FILES['imagem']
        planta.save()
        messages.success(request, 'Planta actualizada!')
        return redirect('/dashboard/')
    return render(request, 'planta_form.html', {'planta': planta})


def planta_eliminar(request, pk):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')
    if request.method != 'POST':
        return redirect('/dashboard/')
    planta = get_object_or_404(Planta, pk=pk, vendedor=user)
    planta.delete()
    messages.success(request, 'Planta eliminada.')
    return redirect('/dashboard/')


def perfil(request):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')

    sucesso = None
    erro = None

    if request.method == 'POST':
        from django.contrib.auth.hashers import make_password
        email = request.POST.get('email', '').strip()

        if email != user.email and Utilizador.objects.filter(email=email).exclude(id=user.id).exists():
            erro = 'Este email já está em uso.'
        else:
            user.nome = request.POST.get('nome', user.nome).strip()
            user.email = email
            user.telefone = request.POST.get('telefone', '')
            user.localizacao = request.POST.get('localizacao', '')
            user.bio = request.POST.get('bio', '')
            user.whatsapp = request.POST.get('whatsapp', '').replace('+', '').replace(' ', '')
            user.instagram = request.POST.get('instagram', '').replace('@', '')
            user.facebook = request.POST.get('facebook', '')
            senha = request.POST.get('senha', '')
            if senha:
                if len(senha) >= 6:
                    user.senha = make_password(senha)
                else:
                    erro = 'A nova senha deve ter pelo menos 6 caracteres.'
            if not erro:
                user.save()
                request.session['utilizador_nome'] = user.nome
                sucesso = 'Perfil actualizado com sucesso!'

    avals = Avaliacao.objects.filter(vendedor=user)
    media = round(sum(a.nota for a in avals) / avals.count(), 1) if avals.exists() else None
    pedidos_recebidos = ItensPedido.objects.filter(planta__vendedor=user).values_list('pedido_id', flat=True).distinct().count()
    plantas_vendidas = ItensPedido.objects.filter(planta__vendedor=user).count()

    return render(request, 'perfil.html', {
        'utilizador':       user,
        'sucesso':          sucesso,
        'erro':             erro,
        'total_plantas':    user.plantas.count() if user.is_vendedor else 0,
        'media_avaliacao':  media,
        'pedidos_recebidos': pedidos_recebidos,
        'plantas_vendidas': plantas_vendidas,
        'total_pedidos':    user.pedidos.count() if user.is_cliente else 0,
        'total_favoritos':  user.favoritos.count() if user.is_cliente else 0,
    })


def perfil_mudar_tipo(request):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')
    if request.method != 'POST':
        return redirect('/perfil/')

    novo = (request.POST.get('tipo') or '').strip()
    if novo not in ('cliente', 'vendedor'):
        messages.error(request, 'Tipo de conta inválido.')
        return redirect('/perfil/')

    user.tipo = novo
    user.save()
    if novo == 'vendedor':
        messages.success(request, 'Agora és vendedor! Já podes publicar as tuas plantas no marketplace.')
    else:
        messages.success(request, 'A tua conta agora está apenas para comprar.')
    return redirect('/perfil/')


def avaliar_vendedor(request, vendedor_id):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')

    from plantas.models import Avaliacao
    from usuarios.models import Utilizador as Util

    try:
        vendedor = Util.objects.get(id=vendedor_id)
    except Util.DoesNotExist:
        return redirect('/marketplace/')

    # Vendedor não pode avaliar a si próprio (redundante mas seguro)
    if user.id == vendedor.id:
        messages.error(request, 'Não podes avaliar o teu próprio perfil.')
        return redirect('/marketplace/')

    avaliacoes = Avaliacao.objects.filter(vendedor=vendedor).select_related('cliente').order_by('-data_avaliacao')
    ja_avaliou = avaliacoes.filter(cliente=user).exists()
    total = avaliacoes.count()
    media = round(sum(a.nota for a in avaliacoes) / total, 1) if total else 0

    erro = None
    if request.method == 'POST' and not ja_avaliou:
        nota = request.POST.get('nota', '')
        comentario = request.POST.get('comentario', '').strip()
        if not nota or not nota.isdigit() or not (1 <= int(nota) <= 5):
            erro = 'Seleciona uma classificação entre 1 e 5 estrelas.'
        else:
            Avaliacao.objects.create(
                cliente=user,
                vendedor=vendedor,
                nota=int(nota),
                comentario=comentario
            )
            messages.success(request, 'Avaliação enviada com sucesso!')
            return redirect(f'/avaliar/{vendedor_id}/')

    return render(request, 'avaliacoes.html', {
        'utilizador': user,
        'vendedor': vendedor,
        'avaliacoes': avaliacoes,
        'ja_avaliou': ja_avaliou,
        'media_nota': media,
        'total_avaliacoes': total,
        'erro': erro,
    })


def mensagens_inbox(request):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')

    from plantas.models import Mensagem
    from django.db.models import Q, Max

    # Obter todos os IDs de utilizadores com quem trocou mensagens
    trocas = Mensagem.objects.filter(
        Q(remetente=user) | Q(destinatario=user)
    ).values_list('remetente_id', 'destinatario_id')

    outros_ids = set()
    for r, d in trocas:
        outros_ids.add(d if r == user.id else r)

    from usuarios.models import Utilizador as Util
    conversas = []
    for oid in outros_ids:
        try:
            outro = Util.objects.get(id=oid)
            ultima = Mensagem.objects.filter(
                Q(remetente=user, destinatario=outro) | Q(remetente=outro, destinatario=user)
            ).order_by('-data_envio').first()
            nao_lida = Mensagem.objects.filter(remetente=outro, destinatario=user, lida=False).exists()
            conversas.append({
                'outro_id': oid,
                'nome': outro.nome,
                'ultima_msg': ultima.mensagem[:40] if ultima else '',
                'nao_lida': nao_lida,
            })
        except Util.DoesNotExist:
            pass

    nao_lidas = sum(1 for c in conversas if c['nao_lida'])
    return render(request, 'mensagens.html', {
        'utilizador': user,
        'conversas': conversas,
        'nao_lidas': nao_lidas,
        'conversa_ativa': None,
    })


def mensagens_conversa(request, outro_id):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')

    from plantas.models import Mensagem
    from usuarios.models import Utilizador as Util
    from django.db.models import Q

    try:
        outro = Util.objects.get(id=outro_id)
    except Util.DoesNotExist:
        return redirect('/mensagens/')

    # Marcar como lidas todas as mensagens recebidas nesta conversa
    Mensagem.objects.filter(remetente=outro, destinatario=user, lida=False).update(lida=True)

    mensagens_list = Mensagem.objects.filter(
        Q(remetente=user, destinatario=outro) | Q(remetente=outro, destinatario=user)
    ).order_by('data_envio')

    # Conversas para sidebar
    trocas = Mensagem.objects.filter(
        Q(remetente=user) | Q(destinatario=user)
    ).values_list('remetente_id', 'destinatario_id')
    outros_ids = set()
    for r, d in trocas:
        outros_ids.add(d if r == user.id else r)
    if outro_id not in outros_ids:
        outros_ids.add(outro_id)

    conversas = []
    for oid in outros_ids:
        try:
            o = Util.objects.get(id=oid)
            ultima = Mensagem.objects.filter(
                Q(remetente=user, destinatario=o) | Q(remetente=o, destinatario=user)
            ).order_by('-data_envio').first()
            conversas.append({
                'outro_id': oid,
                'nome': o.nome,
                'ultima_msg': ultima.mensagem[:40] if ultima else '',
                'nao_lida': Mensagem.objects.filter(remetente=o, destinatario=user, lida=False).exists(),
            })
        except Util.DoesNotExist:
            pass

    nao_lidas = 0
    return render(request, 'mensagens.html', {
        'utilizador': user,
        'conversas': conversas,
        'nao_lidas': nao_lidas,
        'conversa_ativa': outro_id,
        'outro_utilizador': outro,
        'mensagens': mensagens_list,
    })


def mensagens_enviar(request, outro_id):
    user = get_utilizador(request)
    if not user or request.method != 'POST':
        return redirect('/mensagens/')

    from plantas.models import Mensagem
    from usuarios.models import Utilizador as Util

    texto = request.POST.get('mensagem', '').strip()
    audio = request.FILES.get('audio') or request.FILES.get('audio_file')

    if texto or audio:
        try:
            outro = Util.objects.get(id=outro_id)
            Mensagem.objects.create(
                remetente=user,
                destinatario=outro,
                mensagem=texto,
                audio=audio,
                lida=False
            )
        except Util.DoesNotExist:
            pass
    return redirect(f'/mensagens/{outro_id}/')


def mensagem_vendedor(request, vendedor_id):
    """Redireciona para a conversa com o vendedor a partir da página de detalhe"""
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')
    return redirect(f'/mensagens/{vendedor_id}/')


def pedidos_gerir(request):
    user = get_utilizador(request)
    if not user:
        return redirect('/dashboard/')

    filtro = request.GET.get('status', 'todos')
    # Pedidos das plantas deste vendedor
    from django.db.models import Q
    pedidos_ids = ItensPedido.objects.filter(planta__vendedor=user).values_list('pedido_id', flat=True).distinct()
    pedidos = Pedido.objects.filter(id__in=pedidos_ids).select_related('cliente').prefetch_related('itens__planta').order_by('-data_pedido')

    if filtro and filtro != 'todos':
        pedidos = pedidos.filter(status=filtro)

    status_opcoes = [
        ('todos', 'Todos'),
        ('pendente', 'Pendentes'),
        ('confirmado', 'Confirmados'),
        ('entregue', 'Entregues'),
        ('cancelado', 'Cancelados'),
    ]

    todos = Pedido.objects.filter(id__in=pedidos_ids)
    return render(request, 'pedidos_vendedor.html', {
        'utilizador': user,
        'pedidos': pedidos,
        'filtro': filtro,
        'status_opcoes': status_opcoes,
        'total_pedidos': todos.count(),
        'pendentes': todos.filter(status='pendente').count(),
        'confirmados': todos.filter(status='confirmado').count(),
        'entregues': todos.filter(status='entregue').count(),
    })


def pedido_criar(request, planta_id):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')
    if request.method != 'POST':
        return redirect(f'/planta/{planta_id}/')
    planta = get_object_or_404(Planta, pk=planta_id)
    if user == planta.vendedor:
        messages.error(request, 'Não podes encomendar a tua própria planta.')
        return redirect(f'/planta/{planta_id}/')
    try:
        quantidade = max(1, int(request.POST.get('quantidade', 1)))
    except (ValueError, TypeError):
        quantidade = 1
    pedido = Pedido.objects.create(cliente=user)
    ItensPedido.objects.create(pedido=pedido, planta=planta, quantidade=quantidade, preco=planta.preco)
    messages.success(request, f'Pedido #{pedido.id} criado com sucesso!')
    return redirect('/dashboard/')


def favorito_toggle(request, planta_id):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')
    if request.method != 'POST':
        return redirect(f'/planta/{planta_id}/')
    planta = get_object_or_404(Planta, pk=planta_id)
    fav, created = Favorito.objects.get_or_create(cliente=user, planta=planta)
    if not created:
        fav.delete()
        messages.success(request, 'Removido dos favoritos.')
    else:
        messages.success(request, 'Adicionado aos favoritos!')
    return redirect(f'/planta/{planta_id}/')


def pedido_status(request, pedido_id):
    user = get_utilizador(request)
    if not user:
        return redirect('/dashboard/')
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if not pedido.itens.filter(planta__vendedor=user).exists():
        return redirect('/pedidos/gerir/')
    novo_status = request.POST.get('status', '')
    if novo_status in ['pendente', 'confirmado', 'entregue', 'cancelado']:
        pedido.status = novo_status
        pedido.save()
        # Mensagem automática ao cliente
        msgs = {
            'confirmado': f'O teu pedido #{pedido.id} foi confirmado! Estamos a preparar a tua encomenda.',
            'entregue': f'O teu pedido #{pedido.id} foi marcado como entregue. Obrigado pela compra!',
            'cancelado': f'Lamentamos informar que o teu pedido #{pedido.id} foi cancelado. Contacta-nos para mais informações.',
        }
        if novo_status in msgs:
            Mensagem.objects.create(
                remetente=user,
                destinatario=pedido.cliente,
                mensagem=msgs[novo_status]
            )
        messages.success(request, f'Pedido #{pedido.id} actualizado para "{novo_status}".')
    return redirect('/pedidos/gerir/')


def encomendas_cliente(request):
    user = get_utilizador(request)
    if not user:
        return redirect('/login/')

    filtro = request.GET.get('status', 'todos')
    pedidos = Pedido.objects.filter(cliente=user).prefetch_related('itens__planta__vendedor').order_by('-data_pedido')

    if filtro and filtro != 'todos':
        pedidos = pedidos.filter(status=filtro)

    STEPS = [
        ('pendente',   'Pedido feito',  'fa-cart-shopping'),
        ('confirmado', 'Confirmado',    'fa-check'),
        ('entregue',   'Entregue',      'fa-truck'),
    ]
    STEP_ORDER = ['pendente', 'confirmado', 'entregue']

    pedidos_list = []
    for p in pedidos:
        primeiro_item = p.itens.first()
        vendedor = primeiro_item.planta.vendedor if primeiro_item else None
        step_index = STEP_ORDER.index(p.status) + 1 if p.status in STEP_ORDER else 0
        steps_done = STEP_ORDER[:step_index]
        p.vendedor_nome = vendedor.nome if vendedor else '—'
        p.vendedor_id   = vendedor.id   if vendedor else None
        p.timeline      = STEPS
        p.steps_done    = steps_done
        p.step_index    = step_index
        pedidos_list.append(p)

    status_opcoes = [
        ('todos',      'Todos'),
        ('pendente',   'Pendentes'),
        ('confirmado', 'Confirmados'),
        ('entregue',   'Entregues'),
        ('cancelado',  'Cancelados'),
    ]
    return render(request, 'pedidos_cliente.html', {
        'utilizador':    user,
        'pedidos':       pedidos_list,
        'filtro':        filtro,
        'status_opcoes': status_opcoes,
    })
