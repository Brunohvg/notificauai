from django.db import models
from core.model import BaseModel


class Customer(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Nome do Cliente')
    email = models.EmailField(verbose_name='E-mail', db_index=True)
    phone = models.CharField(max_length=30, blank=True, verbose_name='Telefone')
    identification = models.CharField(max_length=20, blank=True, verbose_name='CPF/CNPJ')
    external_id = models.CharField(max_length=100, db_index=True)
    source = models.CharField(max_length=50, verbose_name='Fonte')

    accepts_marketing = models.BooleanField(default=False, verbose_name='Aceita Marketing')
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total Gasto')
    last_order_external_id = models.CharField(max_length=100, blank=True, verbose_name='Último Pedido')
    first_interaction = models.DateTimeField(null=True, blank=True, verbose_name='Primeira Interação')
    created_at_nuvemshop = models.DateTimeField(null=True, blank=True, verbose_name='Criado na Nuvemshop')

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = ('workspace', 'source', 'external_id')

    def __str__(self):
        return self.name


class AddressType(models.TextChoices):
    SHIPPING = 'shipping', 'Entrega'
    BILLING = 'billing', 'Faturação'


class Address(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=AddressType.choices)
    street = models.CharField(max_length=255, verbose_name='Rua')
    number = models.CharField(max_length=50, verbose_name='Número', null=True, blank=True)  # nullable para evitar migração problemática
    floor = models.CharField(max_length=50, blank=True, verbose_name='Andar/Complemento')
    locality = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    city = models.CharField(max_length=100, verbose_name='Cidade')
    province = models.CharField(max_length=100, verbose_name='Estado/Província')
    country = models.CharField(max_length=5, default='BR', verbose_name='País')
    zipcode = models.CharField(max_length=20, verbose_name='CEP')

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f"{self.street}, {self.number or ''} - {self.city}"


class OrderStatus(models.TextChoices):
    PENDING_PAYMENT = 'pending_payment', 'Aguardando Pagamento'
    PROCESSING = 'processing', 'Em Processamento'
    SHIPPED = 'shipped', 'Enviado'
    DELIVERED = 'delivered', 'Entregue'
    CANCELLED = 'cancelled', 'Cancelado'
    REFUNDED = 'refunded', 'Reembolsado'
    PAID = 'paid', 'Pago'
    OPEN = 'open', 'Aberto'


class ShippingStatus(models.TextChoices):
    SHIPPED = 'shipped', 'Enviado'
    NOT_SHIPPED = 'not_shipped', 'Não Enviado'


class Order(BaseModel):
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='orders'
    )
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipping_orders'
    )

    external_id = models.CharField(max_length=100, db_index=True)
    number = models.PositiveIntegerField(
        verbose_name='Número do Pedido', null=True, blank=True
    )  # nullable para não quebrar migração

    source = models.CharField(max_length=50)
    store_id = models.CharField(max_length=30, verbose_name='ID da Loja Nuvemshop', blank=True)

    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING_PAYMENT,
        db_index=True
    )
    payment_status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING_PAYMENT,
        verbose_name='Status do Pagamento'
    )
    payment_method = models.CharField(max_length=50, verbose_name='Forma de Pagamento', blank=True)
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Pago em')

    shipping_status = models.CharField(
        max_length=20,
        choices=ShippingStatus.choices,
        default=ShippingStatus.NOT_SHIPPED,
        verbose_name='Status do Envio'
    )
    

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Subtotal')
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Desconto Total')
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Valor do Frete')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total Pago')

    currency = models.CharField(max_length=10, default='BRL')
    gateway = models.CharField(max_length=100, blank=True, verbose_name='Gateway')
    gateway_id = models.CharField(max_length=100, blank=True, verbose_name='ID do Gateway')

    order_created_at = models.DateTimeField(verbose_name='Criado em')
    paid_by_customer = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Pago pelo Cliente')

    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    raw_payload = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        unique_together = ('workspace', 'source', 'external_id')
        ordering = ['-order_created_at']

    def __str__(self):
        # Use número se existir, senão external_id para facilitar visualização
        num = self.number if self.number else self.external_id
        return f"Pedido #{num} ({self.get_status_display()})"


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
