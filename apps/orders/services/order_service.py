from django.db import transaction
from ..models import Order, Customer
from ..parsers.nuvemshop_parser import NuvemshopParser
# from ..parsers.mercadolivre_parser import MercadoLivreParser
from nuvemshop_client import NuvemshopClient

PARSER_MAPPING = {
    'NUVEMSHOP': NuvemshopParser,
    # 'MERCADOLIVRE': MercadoLivreParser,
}

# Eventos que realmente indicam alterações no pedido
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
    """
    Cria ou atualiza um pedido e cliente a partir de um webhook da Nuvemshop.
    """
    # Filtra eventos irrelevantes
    if webhook_event.event_type not in EVENTS_TO_PROCESS:
        print(f"Ignorando evento: {webhook_event.event_type}")
        return

    source = webhook_event.source  # Ex: 'NUVEMSHOP'
    payload = webhook_event.payload
    external_order_id = payload.get('id')  # ID do pedido na Nuvemshop

    if not external_order_id:
        raise ValueError("ID do pedido não encontrado no payload.")

    # Instancia cliente Nuvemshop
    client = NuvemshopClient(
        store_id=integration.store_id,
        access_token=integration.access_token
    )

    # Busca o pedido completo via API
    order_raw_data = client.orders.get(resource_id=external_order_id)

    # Obtém o parser da fonte (ex: Nuvemshop)
    parser_class = PARSER_MAPPING.get(source)
    if not parser_class:
        raise NotImplementedError(f"Nenhum parser implementado para a fonte: {source}")

    # Transforma o payload bruto em dados padronizados
    parser = parser_class(order_raw_data)
    data = parser.parse()

    customer_data = data['customer']
    order_data = data['order']

    # Cria ou atualiza o cliente
    customer, _ = Customer.objects.update_or_create(
        workspace=webhook_event.workspace,
        external_id=customer_data['external_id'],
        source=source,
        defaults=customer_data
    )

    # Cria ou atualiza o pedido
    Order.objects.update_or_create(
        workspace=webhook_event.workspace,
        external_id=order_data['external_id'],
        source=source,
        defaults={
            'customer': customer,
            'status': order_data['status'],
            'total_amount': order_data['total_amount'],
            'order_created_at': order_data['order_created_at'],
            'raw_payload': payload  # Armazena o payload do webhook original
        }
    )
