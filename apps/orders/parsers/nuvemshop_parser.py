# Em apps/orders/parsers/nuvemshop_parser.py
from decimal import Decimal, InvalidOperation
from .base_parser import BaseParser
from apps.orders.models import Order

class NuvemshopParser(BaseParser):
    """
    Parser especialista e robusto para a Nuvemshop.
    Lida com dados em falta e garante uma saída de dados consistente.
    """

    def _get_status(self) -> str:
        """Determina o status correto do nosso sistema com base na hierarquia da Nuvemshop."""

        if self.payload.get('shipping_status') == 'delivered':
            return Order.Status.DELIVERED

        if self.payload.get('shipping_status') == 'shipped':
            return Order.Status.SHIPPED

        if self.payload.get('payment_status') == 'paid':
            if self.payload.get('next_action') == 'waiting_shipment':
                return Order.Status.PACKED
            return Order.Status.PROCESSING

        if self.payload.get('status') == 'cancelled':
            return Order.Status.CANCELLED

        if self.payload.get('status') == 'refunded':
            return Order.Status.REFUNDED

        if self.payload.get('status') == 'pending_payment':
            return Order.Status.PENDING_PAYMENT

        return Order.Status.PENDING_PAYMENT


    def _safe_get(self, data, key, default=''):
        """Função auxiliar para obter valores de forma segura."""
        return data.get(key, default) if data else default

    def _safe_decimal(self, value, default='0.0'):
        """Função auxiliar para converter para Decimal de forma segura."""
        try:
            return Decimal(value)
        except (InvalidOperation, TypeError):
            return Decimal(default)

    def parse(self) -> dict:
        """
        Método principal que realiza a tradução completa do payload,
        garantindo que nenhum erro de campo em falta ocorra.
        """
        customer_payload = self._safe_get(self.payload, 'customer', {})
        shipping_payload = self._safe_get(self.payload, 'shipping_address', {})
        
        customer_data = {
            'name': self._safe_get(customer_payload, 'name'),
            'email': self._safe_get(customer_payload, 'email'),
            'phone': self._safe_get(customer_payload, 'phone'),
            'identification': self._safe_get(customer_payload, 'identification'),
            'external_id': str(self._safe_get(customer_payload, 'id', '0')),
            'accepts_marketing': self._safe_get(customer_payload, 'accepts_marketing', False),
            'total_spent': self._safe_decimal(self._safe_get(customer_payload, 'total_spent')),
            'last_order_external_id': str(self._safe_get(customer_payload, 'last_order_id', '')),
        }
        
        address_data = {
            'street': self._safe_get(shipping_payload, 'address'),
            'number': self._safe_get(shipping_payload, 'number'),
            'floor': self._safe_get(shipping_payload, 'floor'),
            'locality': self._safe_get(shipping_payload, 'locality'),
            'city': self._safe_get(shipping_payload, 'city'),
            'province': self._safe_get(shipping_payload, 'province'),
            'zipcode': self._safe_get(shipping_payload, 'zipcode'),
        }

        order_data = {
            'external_id': str(self._safe_get(self.payload, 'id', '0')),
            'number': self._safe_get(self.payload, 'number'),
            'total_amount': self._safe_decimal(self._safe_get(self.payload, 'total')),
            'order_created_at': self._safe_get(self.payload, 'created_at'),
            'status': self._get_status(),
            'shipping_carrier': self._safe_get(self.payload, 'shipping_option', ''),
            'tracking_code': self._safe_get(self.payload, 'shipping_tracking_number', ''),

            'paid_at': self._safe_get(self.payload, 'paid_at'),  # novo
            'closed_at': self._safe_get(self.payload, 'closed_at'),  # novo
            'shipping_status': self._safe_get(self.payload, 'shipping_status'),  # novo
        }
        
        items_data = [
            {
                'external_product_id': str(item.get('product_id', '0')),
                'product_name': item.get('name', 'Produto sem nome'),
                'quantity': item.get('quantity', 1),
                'price': self._safe_decimal(item.get('price'))
            } for item in self.payload.get('products', [])
        ]
        
        return {
            'customer': customer_data,
            'shipping_address': address_data,
            'order': order_data,
            'items': items_data,
            'source': 'NUVEMSHOP'
        }