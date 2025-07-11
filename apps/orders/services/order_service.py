from django.db import transaction
from ..models import Order, Customer, Address, OrderItem
from ..parsers.nuvemshop_parser import NuvemshopParser
from nuvemshop_client import NuvemshopClient

PARSER_MAPPING = {
    'NUVEMSHOP': NuvemshopParser,
}

EVENTS_TO_PROCESS = {
    "order/created",
    "order/updated",
    "order/paid",
    "order/fulfilled",
    "order/cancelled",
    "order/edited",
}


@transaction.atomic
def create_order_from_webhook(webhook_event, integration):
    if webhook_event.event_type not in EVENTS_TO_PROCESS:
        print(f"Ignorando evento: {webhook_event.event_type}")
        return

    source = webhook_event.source
    payload = webhook_event.payload
    external_order_id = payload.get('id')
    if not external_order_id:
        raise ValueError("ID do pedido não encontrado no payload.")

    client = NuvemshopClient(store_id=integration.store_id, access_token=integration.access_token)
    order_raw_data = client.orders.get(resource_id=external_order_id)

    parser_class = PARSER_MAPPING.get(source)
    if not parser_class:
        raise NotImplementedError(f"Nenhum parser implementado para a fonte: {source}")

    parser = parser_class(order_raw_data)
    data = parser.parse()

    customer_data = data['customer']
    order_data = data['order']
    items_data = data.get('items', [])
    shipping_address_data = order_data.pop('shipping_address', None)
    billing_address_data = customer_data.pop('billing_address', None)

    # Cria ou atualiza cliente
    customer, _ = Customer.objects.update_or_create(
        workspace=webhook_event.workspace,
        external_id=customer_data['external_id'],
        source=source,
        defaults=customer_data
    )

    # Cria ou atualiza endereço de faturamento (billing)
    if billing_address_data:
        Address.objects.update_or_create(
            workspace=webhook_event.workspace,  # Atribui workspace obrigatório
            customer=customer,
            address_type='billing',
            street=billing_address_data.get('street', ''),
            number=billing_address_data.get('number', ''),
            defaults={
                'floor': billing_address_data.get('floor', ''),
                'locality': billing_address_data.get('locality', ''),
                'city': billing_address_data.get('city', ''),
                'province': billing_address_data.get('province', ''),
                'zipcode': billing_address_data.get('zipcode', ''),
                'country': billing_address_data.get('country', 'BR'),
            }
        )

    # Cria ou atualiza endereço de entrega (shipping)
    if shipping_address_data:
        shipping_address, _ = Address.objects.update_or_create(
            workspace=webhook_event.workspace,  # Atribui workspace obrigatório
            customer=customer,
            address_type='shipping',
            street=shipping_address_data.get('street', '') or shipping_address_data.get('address', ''),
            number=shipping_address_data.get('number', ''),
            defaults={
                'floor': shipping_address_data.get('floor', ''),
                'locality': shipping_address_data.get('locality', ''),
                'city': shipping_address_data.get('city', ''),
                'province': shipping_address_data.get('province', ''),
                'zipcode': shipping_address_data.get('zipcode', ''),
                'country': shipping_address_data.get('country', 'BR'),
            }
        )
    else:
        shipping_address = None

    # Cria ou atualiza pedido
    order, _ = Order.objects.update_or_create(
        workspace=webhook_event.workspace,
        external_id=order_data['external_id'],
        source=source,
        defaults={
            'customer': customer,
            'shipping_address': shipping_address,
            **order_data,
            'raw_payload': payload,
        }
    )

    # Atualiza itens do pedido: limpa os antigos e cria os novos (pode ser otimizado)
    order.items.all().delete()
    order_items = [
        OrderItem(
            workspace=webhook_event.workspace,  # <-- Atribui workspace obrigatório aqui também!
            order=order,
            external_product_id=item['external_product_id'],
            product_name=item['product_name'],
            quantity=item['quantity'],
            price=item['price'],
        )
        for item in items_data
    ]
    OrderItem.objects.bulk_create(order_items)
