# Create your models here.
from django.db import models
from core.model import BaseModel # Usando nosso modelo base

class Customer(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Nome do Cliente')
    email = models.EmailField(verbose_name='E-mail', db_index=True)
    phone = models.CharField(max_length=30, blank=True, verbose_name='Telefone')
    external_id = models.CharField(max_length=100, db_index=True)
    source = models.CharField(max_length=50, verbose_name='Fonte') # Ex: 'NUVEMSHOP'

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = ('workspace', 'source', 'external_id')

    def __str__(self):
        return self.name

class Order(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregue'),
        ('cancelled', 'Cancelado'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    source = models.CharField(max_length=50, verbose_name='Fonte do Pedido')
    external_id = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_created_at = models.DateTimeField(verbose_name='Data de Criação (Origem)')
    raw_payload = models.JSONField(blank=True, null=True) # Para auditoria e depuração

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        unique_together = ('workspace', 'source', 'external_id')
        ordering = ['-order_created_at']

    def __str__(self):
        return f"Pedido #{self.external_id} de {self.source}"