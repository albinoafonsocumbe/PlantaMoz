from django.db import models
from usuarios.models import Utilizador

class Planta(models.Model):
    CATEGORIA_CHOICES = [
        ('ornamental', 'Ornamental'),
        ('medicinal',  'Medicinal'),
        ('fruteira',   'Fruteira'),
        ('aromatica',  'Aromática'),
    ]

    nome        = models.CharField(max_length=100)
    descricao   = models.TextField(blank=True, null=True)
    preco       = models.DecimalField(max_digits=10, decimal_places=2)
    categoria   = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, blank=True, null=True)
    imagem      = models.ImageField(upload_to='plantas/', blank=True, null=True)
    vendedor    = models.ForeignKey(Utilizador, on_delete=models.CASCADE, related_name='plantas')
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'plantas'

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    STATUS_CHOICES = [('pendente', 'Pendente'), ('confirmado', 'Confirmado'), ('entregue', 'Entregue'), ('cancelado', 'Cancelado')]

    cliente     = models.ForeignKey(Utilizador, on_delete=models.CASCADE, related_name='pedidos')
    data_pedido = models.DateTimeField(auto_now_add=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')

    class Meta:
        db_table = 'pedidos'

    def __str__(self):
        return f'Pedido {self.id} - {self.cliente.nome}'

    @property
    def total(self):
        return sum(i.subtotal for i in self.itens.all())


class ItensPedido(models.Model):
    pedido    = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    planta    = models.ForeignKey(Planta, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    preco     = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'itens_pedido'

    @property
    def subtotal(self):
        return self.quantidade * self.preco


class Avaliacao(models.Model):
    cliente   = models.ForeignKey(Utilizador, on_delete=models.CASCADE, related_name='avaliacoes_feitas')
    vendedor  = models.ForeignKey(Utilizador, on_delete=models.CASCADE, related_name='avaliacoes_recebidas')
    nota      = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'avaliacoes'
        unique_together = ('cliente', 'vendedor')  # um cliente, uma avaliação por vendedor


class Mensagem(models.Model):
    remetente    = models.ForeignKey(Utilizador, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey(Utilizador, on_delete=models.CASCADE, related_name='mensagens_recebidas')
    mensagem     = models.TextField(blank=True)
    audio        = models.FileField(upload_to='audios/', blank=True, null=True)
    lida         = models.BooleanField(default=False)
    data_envio   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mensagens'


class Favorito(models.Model):
    cliente = models.ForeignKey(Utilizador, on_delete=models.CASCADE, related_name='favoritos')
    planta  = models.ForeignKey(Planta, on_delete=models.CASCADE, related_name='favoritos')

    class Meta:
        db_table = 'favoritos'
        unique_together = ('cliente', 'planta')  # sem duplicados
