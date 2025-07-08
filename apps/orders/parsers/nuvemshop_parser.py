from .base_parser import BaseParser

class NuvemshopParser(BaseParser):
    """
    O tradutor especialista em dados da Nuvemshop.
    """
    def parse(self) -> dict:
        # A lógica de "leitura" do JSON da Nuvemshop vive aqui, isolada.
        customer_data = self.payload.get('customer', {})
        
        # Traduz os dados para o nosso formato padronizado
        standardized_data = {
            'customer': {
                'name': customer_data.get('name'),
                'email': customer_data.get('email'),
                'phone': customer_data.get('phone'),
                'external_id': str(customer_data.get('id')),
            },
            'order': {
                'external_id': str(self.payload.get('id')),
                'total_amount': self.payload.get('total'),
                'status': self.payload.get('status'), # Ex: 'paid', 'shipped'
                'order_created_at': self.payload.get('created_at'),
            },
            'source': 'NUVEMSHOP'
        }
        return standardized_data