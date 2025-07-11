from django.db import models
from apps.common.models import BaseModel


class Customer(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Nome do Cliente')
    email = models.EmailField(verbose_name='E-mail', db_index=True)
    phone = models.CharField(max_length=30, blank=True, verbose_name='Telefone')
    external_id = models.CharField(max_length=100, db_index=True)  # <- sem unique=True
    source = models.CharField(max_length=50, verbose_name='Fonte')

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
    number = models.CharField(max_length=50, verbose_name='Número')
    city = models.CharField(max_length=100, verbose_name='Cidade')
    province = models.CharField(max_length=100, verbose_name='Estado/Província')
    zipcode = models.CharField(max_length=20, verbose_name='CEP')

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f"{self.street}, {self.number} - {self.city}"


class OrderStatus(models.TextChoices):
    PENDING_PAYMENT = 'pending_payment', 'Aguardando Pagamento'
    PROCESSING = 'processing', 'Em Processamento'
    SHIPPED = 'shipped', 'Enviado'
    DELIVERED = 'delivered', 'Entregue'
    CANCELLED = 'cancelled', 'Cancelado'
    REFUNDED = 'refunded', 'Reembolsado'


class Order(BaseModel):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='shipping_orders'
    )
    source = models.CharField(max_length=50)
    external_id = models.CharField(max_length=100, db_index=True)  # <- sem unique=True
    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING_PAYMENT,
        db_index=True
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_created_at = models.DateTimeField()
    shipping_carrier = models.CharField(max_length=100, blank=True)
    tracking_code = models.CharField(max_length=100, blank=True)
    tracking_url = models.URLField(max_length=500, blank=True)
    raw_payload = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        unique_together = ('workspace', 'source', 'external_id')
        ordering = ['-order_created_at']

    def __str__(self):
        return f"Pedido #{self.external_id} ({self.get_status_display()})"


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
