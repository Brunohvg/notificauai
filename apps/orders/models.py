# Em apps/orders/models.py
# -----------------------------------------------------------------------------
# Este ficheiro define a estrutura de dados completa para o app de Pedidos.
# A arquitetura é projetada para ser agnóstica da plataforma, robusta
# e preparada para futuras funcionalidades de CRM e marketing.
# -----------------------------------------------------------------------------

from django.db import models
from core.model import BaseModel # Ou o caminho correto para o seu BaseModel

# -----------------------------------------------------------------------------
# Modelo Cliente (Com todos os seus campos de CRM/Marketing)
# -----------------------------------------------------------------------------
class Customer(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Nome do Cliente')
    email = models.EmailField(verbose_name='E-mail', db_index=True)
    phone = models.CharField(max_length=30, blank=True, verbose_name='Telefone')
    identification = models.CharField(max_length=20, blank=True, verbose_name='CPF/CNPJ')
    
    # Rastreabilidade
    external_id = models.CharField(max_length=100, db_index=True)
    source = models.CharField(max_length=50, verbose_name='Fonte')

    # Campos para CRM e Marketing, conforme a sua visão de produto
    accepts_marketing = models.BooleanField(default=False, verbose_name='Aceita Marketing')
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total Gasto')
    last_order_external_id = models.CharField(max_length=100, blank=True, verbose_name='ID do Último Pedido')
    
    # Timestamps da plataforma de origem
    first_interaction = models.DateTimeField(null=True, blank=True, verbose_name='Primeira Interação')
    created_at_nuvemshop = models.DateTimeField(null=True, blank=True, verbose_name='Criado na Nuvemshop')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = ('workspace', 'source', 'external_id')

    def __str__(self):
        return self.name

# -----------------------------------------------------------------------------
# Modelo Endereço
# -----------------------------------------------------------------------------
class Address(BaseModel):
    class AddressType(models.TextChoices):
        SHIPPING = 'shipping', 'Entrega'
        BILLING = 'billing', 'Faturação'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=AddressType.choices)
    street = models.CharField(max_length=255, verbose_name='Rua')
    number = models.CharField(max_length=50, blank=True, verbose_name='Número')
    floor = models.CharField(max_length=50, blank=True, verbose_name='Andar/Complemento')
    locality = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    city = models.CharField(max_length=100, verbose_name='Cidade')
    province = models.CharField(max_length=100, verbose_name='Estado/Província')
    zipcode = models.CharField(max_length=20, verbose_name='CEP')

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f"{self.street}, {self.number or ''} - {self.city}"

# -----------------------------------------------------------------------------
# Modelo Pedido (Com status unificado e campos de envio)
# -----------------------------------------------------------------------------
class Order(BaseModel):
    class Status(models.TextChoices):
        PENDING_PAYMENT = 'pending_payment', 'Aguardando Pagamento'
        PROCESSING = 'processing', 'Em Processamento'
        PACKED = 'packed', 'Embalado'
        SHIPPED = 'shipped', 'Enviado'
        DELIVERED = 'delivered', 'Entregue'
        CANCELLED = 'cancelled', 'Cancelado'
        REFUNDED = 'refunded', 'Reembolsado'

    # Relacionamentos
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipping_orders')

    # Identificação do pedido
    external_id = models.CharField(max_length=100, db_index=True)
    number = models.PositiveIntegerField(verbose_name='Número do Pedido', null=True, blank=True)
    source = models.CharField(max_length=50)

    # Status e acompanhamento
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING_PAYMENT, db_index=True)
    shipping_status = models.CharField(max_length=30, blank=True, null=True, verbose_name='Status de Envio')

    # Valores
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Total')

    # Envio
    shipping_carrier = models.CharField(max_length=100, blank=True, verbose_name='Transportadora')
    tracking_code = models.CharField(max_length=100, blank=True, null=True, verbose_name='Código de Rastreio')

    # Datas
    order_created_at = models.DateTimeField(verbose_name='Criado em (Origem)')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Pago em')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fechado em (Origem)')

    # Técnicos / Logs
    raw_payload = models.JSONField(blank=True, null=True, help_text="O payload original do webhook para auditoria.")

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        unique_together = ('workspace', 'source', 'external_id')
        ordering = ['-order_created_at']

    def __str__(self):
        num = self.number if self.number else self.external_id
        return f"Pedido #{num} ({self.get_status_display()})"


# -----------------------------------------------------------------------------
# Modelo Item do Pedido
# -----------------------------------------------------------------------------
class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    external_product_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"