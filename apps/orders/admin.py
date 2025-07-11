# Em apps/orders/admin.py
# -----------------------------------------------------------------------------
# Este ficheiro configura como os modelos do app Orders são exibidos e
# geridos no painel de administração do Django. Uma boa configuração do Admin
# é crucial para a gestão, depuração e visualização dos dados.
# -----------------------------------------------------------------------------

from django.contrib import admin
from .models import Customer, Address, Order, OrderItem

# -----------------------------------------------------------------------------
# Inlines: Permitem editar modelos relacionados na mesma página do modelo pai.
# -----------------------------------------------------------------------------

class AddressInline(admin.TabularInline):
    """
    Permite visualizar e adicionar endereços diretamente na página de um Cliente.
    """
    model = Address
    extra = 0  # Não mostra formulários de endereço em branco por padrão
    fields = ('address_type', 'street', 'number', 'city', 'province', 'zipcode')
    
class OrderItemInline(admin.TabularInline):
    """
    Mostra os itens de um pedido diretamente na página de detalhe do Pedido.
    Estes campos são somente leitura, pois refletem os dados da fonte original.
    """
    model = OrderItem
    extra = 0
    # MELHORIA: Todos os campos são de um sistema externo, então são somente leitura.
    readonly_fields = ('external_product_id', 'product_name', 'quantity', 'price')
    can_delete = False # Impede a exclusão acidental de itens de um pedido

    def has_add_permission(self, request, obj=None):
        # Impede a adição de novos itens manualmente através do admin.
        return False

# -----------------------------------------------------------------------------
# ModelAdmins: Configurações de exibição para cada modelo.
# -----------------------------------------------------------------------------

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Cliente.
    """
    list_display = ('name', 'email', 'source', 'workspace', 'total_spent_formatted')
    search_fields = ('name', 'email', 'external_id', 'workspace__name')
    list_filter = ('source', 'workspace')
    readonly_fields = ('external_id', 'source', 'total_spent', 'last_order_external_id', 'first_interaction', 'created_at_nuvemshop')
    
    # Exibe os endereços do cliente na mesma página, para fácil visualização.
    inlines = [AddressInline]

    def total_spent_formatted(self, obj):
        # O seu método de formatação, seguro e funcional.
        return f"R$ {obj.total_spent:.2f}"
    total_spent_formatted.short_description = "Total Gasto"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Pedido.
    """
    list_display = ('__str__', 'customer', 'status', 'total_amount_formatted', 'order_created_at', 'workspace')
    list_filter = ('status', 'source', 'workspace')
    search_fields = ('external_id', 'number', 'customer__name', 'tracking_code')
    date_hierarchy = 'order_created_at'
    
    # MELHORIA: A maioria dos campos vem de uma fonte externa, então são somente leitura.
    # Apenas o status 'interno' pode ser alterado por um admin, se necessário.
    readonly_fields = (
        'customer', 'shipping_address', 'external_id', 'number', 'source',
        'total_amount', 'shipping_carrier', 'tracking_code', 'order_created_at',
        'created_at', 'updated_at', 'raw_payload'
    )
    
    # Exibe os itens do pedido na mesma página.
    inlines = [OrderItemInline]

    # MELHORIA de Performance: Para modelos com muitos clientes, isto substitui
    # um <select> por um campo de busca, tornando a página muito mais rápida.
    raw_id_fields = ('customer', 'shipping_address')

    def total_amount_formatted(self, obj):
        return f"R$ {obj.total_amount:.2f}"
    total_amount_formatted.short_description = "Valor Total"

# Embora Address e OrderItem sejam inlines, registá-los separadamente
# permite que eles sejam pesquisados e visualizados de forma global no admin.

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Endereço.
    """
    list_display = ('customer', 'address_type', 'street', 'city', 'province', 'zipcode')
    search_fields = ('customer__name', 'street', 'city', 'zipcode')
    list_filter = ('address_type', 'province')
    raw_id_fields = ('customer',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para o modelo Item do Pedido.
    """
    list_display = ('product_name', 'order_link', 'quantity', 'price_formatted')
    search_fields = ('product_name', 'order__external_id')
    readonly_fields = ('order', 'external_product_id', 'product_name', 'quantity', 'price')
    raw_id_fields = ('order',)

    def price_formatted(self, obj):
        return f"R$ {obj.price:.2f}"
    price_formatted.short_description = "Preço"

    def order_link(self, obj):
        # MELHORIA: Adiciona um link direto para a página do pedido.
        from django.urls import reverse
        from django.utils.html import format_html
        link = reverse("admin:orders_order_change", args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', link, obj.order)
    order_link.short_description = 'Pedido'