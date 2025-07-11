from decimal import Decimal
from dateutil.parser import isoparse

from .base_parser import BaseParser


class NuvemshopParser(BaseParser):
    """
    Tradutor especialista em dados da Nuvemshop.
    """

    def parse(self) -> dict:
        payload = self.payload

        customer = payload.get('customer', {})

        # Funções para conversão segura
        def safe_decimal(value):
            try:
                return Decimal(value)
            except Exception:
                return Decimal('0.00')

        def safe_datetime(value):
            try:
                return isoparse(value) if value else None
            except Exception:
                return None

        # Billing address (cliente)
        billing_address = {
            'street': customer.get('billing_address', ''),
            'number': customer.get('billing_number', ''),
            'floor': customer.get('billing_floor', ''),
            'locality': customer.get('billing_locality', ''),
            'city': customer.get('billing_city', ''),
            'province': customer.get('billing_province', ''),
            'zipcode': customer.get('billing_zipcode', ''),
            'country': customer.get('billing_country', 'BR'),
        }

        # Shipping address (pedido)
        shipping_address = payload.get('shipping_address', {})
        if not shipping_address:
            shipping_address = billing_address  # fallback

        # Itens do pedido
        raw_items = payload.get('products', [])
        items = []
        for item in raw_items:
            items.append({
                'external_product_id': str(item.get('variant_id', '')),
                'product_name': item.get('name', ''),
                'quantity': int(item.get('quantity', 0)),
                'price': safe_decimal(item.get('price', '0.00')),
            })

        standardized_data = {
            'customer': {
                'name': customer.get('name'),
                'email': customer.get('email'),
                'phone': customer.get('phone') or '',
                'identification': customer.get('identification') or '',
                'external_id': str(customer.get('id')),
                'accepts_marketing': customer.get('accepts_marketing', False),
                'total_spent': safe_decimal(customer.get('total_spent', '0.00')),
                'last_order_external_id': str(customer.get('last_order_id')) if customer.get('last_order_id') else '',
                'first_interaction': safe_datetime(customer.get('first_interaction')),
                'created_at_nuvemshop': safe_datetime(customer.get('created_at')),
                # Endereço de faturamento para criar Address tipo billing
                'billing_address': billing_address,
            },
            'order': {
                'external_id': str(payload.get('id')),
                'number': int(payload.get('number', 0)),
                'store_id': str(payload.get('store_id')),
                'source': 'NUVEMSHOP',
                'status': payload.get('status'),
                'payment_status': payload.get('payment_status', ''),
                'payment_method': payload.get('payment_details', {}).get('method', ''),
                'paid_at': safe_datetime(payload.get('paid_at')),
                'shipping_status': payload.get('shipping_status', ''),
                'subtotal': safe_decimal(payload.get('subtotal', '0.00')),
                'discount_total': safe_decimal(payload.get('discount', '0.00')),
                'shipping_total': safe_decimal(payload.get('previous_total_shipping_cost', {}).get('consumer_cost', '0.00')),
                'total_amount': safe_decimal(payload.get('total', '0.00')),
                'currency': payload.get('currency', 'BRL'),
                'gateway': payload.get('gateway_name', '') or payload.get('gateway', ''),
                'gateway_id': payload.get('gateway_id', ''),
                'order_created_at': safe_datetime(payload.get('created_at')),
                'paid_by_customer': safe_decimal(payload.get('total_paid_by_customer', '0.00')),
                'client_ip': payload.get('client_details', {}).get('browser_ip', ''),
                'user_agent': payload.get('client_details', {}).get('user_agent', ''),
                'shipping_address': {
                    'street': shipping_address.get('address', ''),
                    'number': shipping_address.get('number', ''),
                    'floor': shipping_address.get('floor', ''),
                    'locality': shipping_address.get('locality', ''),
                    'city': shipping_address.get('city', ''),
                    'province': shipping_address.get('province', ''),
                    'zipcode': shipping_address.get('zipcode', ''),
                    'country': shipping_address.get('country', 'BR'),
                },
            },
            'items': items,
        }

        return standardized_data
