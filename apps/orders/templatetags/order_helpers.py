# ARQUIVO: apps/orders/templatetags/order_helpers.py
# OBJETIVO: Definir filtros personalizados para usar nos templates do app de pedidos.

from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplica o valor (value) pelo argumento (arg)."""
    try:
        # Tenta converter para float para garantir que a multiplicação funcione
        return float(value) * float(arg)
    except (ValueError, TypeError):
        # Retorna uma string vazia se a conversão falhar
        return ''

@register.filter(name='status_to_badge')
def status_to_badge(status_key):
    """Converte a chave do status do pedido em uma classe de badge Bootstrap."""
    status_map = {
        'pending_payment': 'bg-warning text-dark',
        'processing': 'bg-info text-dark',
        'packed': 'bg-secondary',
        'shipped': 'bg-primary',
        'delivered': 'bg-success',
        'cancelled': 'bg-danger',
        'refunded': 'bg-dark',
    }
    return status_map.get(status_key, 'bg-light text-dark')