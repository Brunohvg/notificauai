# Em apps/orders/services/order_service.py
# -----------------------------------------------------------------------------
# Versão final e correta do serviço de pedidos, implementando a lógica de
# "buscar antes de processar" que é essencial para o fluxo da Nuvemshop.
# -----------------------------------------------------------------------------

from django.db import transaction
from ..models import Order, Customer, OrderItem, Address
from ..parsers.nuvemshop_parser import NuvemshopParser
from nuvemshop_client.exception import NuvemshopClientError # O nosso cliente de API
from nuvemshop_client import NuvemshopClient
PARSER_MAPPING = {
    'NUVEMSHOP': NuvemshopParser,
}

@transaction.atomic
def create_order_from_webhook(webhook_event, integration):
    """
    Cria ou atualiza um pedido a partir de um webhook da Nuvemshop.

    Fluxo de Trabalho:
    1. Recebe o ID do pedido do payload do webhook.
    2. Usa o cliente da API para buscar os dados completos do pedido na Nuvemshop.
    3. Passa os dados completos para o parser para tradução.
    4. Cria ou atualiza os modelos (Customer, Order, etc.) no banco de dados.
    """
    source = webhook_event.source
    payload = webhook_event.payload
    
    # 1. Pega o ID do pedido a partir do payload do webhook
    external_order_id = payload.get('id')
    if not external_order_id:
        raise ValueError("ID do pedido não encontrado no payload do webhook.")

    try:
        # 2. USA O CLIENTE PARA BUSCAR OS DADOS COMPLETOS NA API
        client = NuvemshopClient(
            store_id=integration.store_id,
            access_token=integration.access_token
        )
        # Supondo que o seu cliente tenha um método .get() para pedidos
        order_full_data = client.orders.get(external_order_id)

    except NuvemshopClientError as e:
        # Se a busca na API falhar, levanta um erro para ser tratado
        raise ValueError(f"Falha ao buscar os dados do pedido #{external_order_id} na API: {e}")

    # 3. Passa os DADOS COMPLETOS (order_full_data) para o parser
    parser_class = PARSER_MAPPING.get(source)
    if not parser_class:
        raise NotImplementedError(f"Nenhum parser implementado para a fonte: {source}")

    parser = parser_class(order_full_data)
    data = parser.parse()

    # A partir daqui, a lógica é a mesma, usando os dados agora completos
    customer_data = data['customer']
    order_data = data['order']
    items_data = data['items']
    address_data = data['shipping_address']

    # 4. Cria ou atualiza o Cliente, Endereço, Pedido e Itens
    customer, _ = Customer.objects.update_or_create(
        workspace=webhook_event.workspace,
        external_id=customer_data['external_id'],
        source=source,
        defaults=customer_data
    )
    
    if address_data.get('zipcode') and address_data.get('street'):
        address, _ = Address.objects.update_or_create(
            customer=customer, address_type=Address.AddressType.SHIPPING,
            zipcode=address_data['zipcode'], street=address_data['street'],
            defaults={**address_data, 'workspace': webhook_event.workspace}
        )
    else:
        address = None

    order_obj, created = Order.objects.update_or_create(
        workspace=webhook_event.workspace, external_id=order_data['external_id'], source=source,
        defaults={'customer': customer, 'shipping_address': address, 'raw_payload': order_full_data, **order_data}
    )

    if items_data:
        if not created:
            order_obj.items.all().delete()
        
        order_items = [
            OrderItem(order=order_obj, workspace=webhook_event.workspace, **item_data)
            for item_data in items_data
        ]
        OrderItem.objects.bulk_create(order_items)

    return order_obj