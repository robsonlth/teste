from django.db import models
from accounts.models import User  # usando seu modelo de usuário customizado


class Familia(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Família'
        verbose_name_plural = 'Famílias'


class Produto(models.Model):
    nome = models.CharField(max_length=50)
    peso = models.DecimalField(max_digits=10, decimal_places=3)
    volume = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    familia = models.ForeignKey(
        Familia, 
        related_name='produtos', 
        on_delete=models.PROTECT
    )
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'


class Pedido(models.Model):
    # Relacionando pedido com seu modelo User
    usuario = models.ForeignKey(
        User, 
        related_name='pedidos_logistica', 
        on_delete=models.CASCADE,
        null=True, 
        blank=True  # Caso nem todos os pedidos precisem ter usuário associado
    )
    nf = models.IntegerField(verbose_name='Nota Fiscal')
    observacao = models.CharField(max_length=100, blank=True, null=True)
    dtpedido = models.DateField(verbose_name='Data do Pedido')
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pedido {self.id} - NF {self.nf}"
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']


class ProdutoPedido(models.Model):
    produto = models.ForeignKey(
        Produto, 
        related_name='itens_pedido', 
        on_delete=models.CASCADE
    )
    pedido = models.ForeignKey(
        Pedido, 
        related_name='itens', 
        on_delete=models.CASCADE
    )
    quantidade = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.produto.nome} - Pedido {self.pedido.id}"
    
    class Meta:
        unique_together = ('produto', 'pedido')
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens dos Pedidos'


class Rota(models.Model):
    STATUS_CHOICES = [
        ('PLANEJADA', 'Planejada'),
        ('EM_EXECUCAO', 'Em execução'),
        ('CONCLUIDA', 'Concluída'),
    ]
    
    data_rota = models.DateField()
    capacidade_max = models.DecimalField(
        max_digits=10, 
        decimal_places=3,
        verbose_name='Capacidade Máxima'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PLANEJADA'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Rota {self.id} - {self.data_rota}"
    
    @property
    def peso_total_pedidos(self):
        """Calcula o peso total dos produtos nos pedidos da rota"""
        peso_total = 0
        for rota_pedido in self.pedidos.all():
            for item in rota_pedido.pedido.itens.all():
                peso_total += item.produto.peso * item.quantidade
        return peso_total
    
    class Meta:
        verbose_name = 'Rota'
        verbose_name_plural = 'Rotas'
        ordering = ['-created_at']


class RotaPedido(models.Model):
    rota = models.ForeignKey(
        Rota, 
        related_name='pedidos', 
        on_delete=models.CASCADE
    )
    pedido = models.ForeignKey(
        Pedido, 
        related_name='rotas', 
        on_delete=models.CASCADE
    )
    ordem_entrega = models.PositiveIntegerField(verbose_name="Ordem de Entrega")
    entregue = models.BooleanField(default=False)
    data_entrega = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Rota {self.rota.id} - Pedido {self.pedido.id} (Ordem: {self.ordem_entrega})"
    
    class Meta:
        unique_together = ('rota', 'pedido')
        verbose_name = 'Pedido da Rota'
        verbose_name_plural = 'Pedidos das Rotas'
        ordering = ['rota', 'ordem_entrega']


class RotaTrajeto(models.Model):
    rota = models.ForeignKey(
        Rota, 
        related_name='trajetos', 
        on_delete=models.CASCADE
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=6)  # Ajustado para 10 dígitos
    longitude = models.DecimalField(max_digits=10, decimal_places=6)  # Ajustado para 10 dígitos
    datahora = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Trajeto Rota {self.rota.id} - {self.datahora}"
    
    class Meta:
        verbose_name = 'Trajeto da Rota'
        verbose_name_plural = 'Trajetos das Rotas'
        ordering = ['rota', 'datahora']