from django.db import transaction
from ..models import Order, Customer
from ..parsers.nuvemshop_parser import NuvemshopParser
#from ..parsers.mercadolivre_parser import MercadoLivreParser # Futuro

# Mapeia a origem a um parser específico
PARSER_MAPPING = {
    'NUVEMSHOP': NuvemshopParser,
    #'MERCADOLIVRE': MercadoLivreParser,
}

@transaction.atomic
def create_order_from_webhook(webhook_event):
    """
    Orquestra a criação de um pedido a partir de um evento de webhook.
    """
    source = webhook_event.source
    payload = webhook_event.payload
    
    # 1. Seleciona o parser correto com base na fonte do evento
    parser_class = PARSER_MAPPING.get(source)
    if not parser_class:
        raise NotImplementedError(f"Nenhum parser implementado para a fonte: {source}")

    # 2. Usa o parser para traduzir os dados
    parser = parser_class(payload)
    standardized_data = parser.parse()
    
    # 3. Usa os dados padronizados para criar os objetos no banco
    customer_info = standardized_data['customer']
    order_info = standardized_data['order']
    
    # Cria ou atualiza o cliente
    customer, _ = Customer.objects.update_or_create(
        workspace=webhook_event.workspace,
        external_id=customer_info['external_id'],
        source=source,
        defaults=customer_info
    )
    
    # Cria ou atualiza o pedido
    Order.objects.update_or_create(
        workspace=webhook_event.workspace,
        external_id=order_info['external_id'],
        source=source,
        defaults={
            'customer': customer,
            'status': order_info['status'],
            'total_amount': order_info['total_amount'],
            'order_created_at': order_info['order_created_at'],
            'raw_payload': payload # Guarda o original para referência
        }
    )