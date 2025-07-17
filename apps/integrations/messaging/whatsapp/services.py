from .models import WhatsappIntegration
from common.utils.responses import create_response 

def check_existing_integration(phone):
    """
    Verifica se já existe uma integração com o número de telefone informado.
    Retorna uma resposta indicando erro se já existir.
    """
    try:
        integration = WhatsappIntegration.objects.get(phone_number=phone)
        #rint(f"Número já registrado: {integration.phone_number}")
        return create_response(
            success=False,
            message='Número já está vinculado a uma integração existente.',
            status_code=409  # 409 Conflict
        )
    except WhatsappIntegration.DoesNotExist:
        #print('Nenhuma integração encontrada para este número.')
        return None  # Ou pode deixar a função não retornar nada explicitamente
