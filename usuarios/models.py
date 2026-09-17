from django.db import models

TIPO_CHOICES = [
    ('cliente', 'Cliente'),
    ('vendedor', 'Vendedor'),
]

class Utilizador(models.Model):
    nome         = models.CharField(max_length=100)
    email        = models.EmailField(max_length=100, unique=True)
    senha        = models.CharField(max_length=255)
    tipo         = models.CharField(max_length=10, choices=TIPO_CHOICES, default='cliente')
    telefone     = models.CharField(max_length=20, blank=True, null=True)
    localizacao  = models.CharField(max_length=100, blank=True, null=True)
    whatsapp     = models.CharField(max_length=20, blank=True, null=True)
    instagram    = models.CharField(max_length=100, blank=True, null=True)
    facebook     = models.CharField(max_length=100, blank=True, null=True)
    bio          = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'utilizadores'

    def __str__(self):
        return self.nome

    @property
    def is_vendedor(self):
        return self.tipo == 'vendedor'

    @property
    def is_cliente(self):
        return self.tipo == 'cliente'
