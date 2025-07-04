import secrets
import json
from django.http import HttpRequest, HttpResponse
from django.db import transaction

# Funções e modelos do nosso projeto
from common.utils.responses import create_response
from apps.integrations.models import WebhookEvent, Integration
from .models import NuvemshopIntegration
from .auth import exchange_code_for_token
from .exceptions import NuvemshopAPIError

@transaction.atomic
def finalize_nuvemshop_integration(code: str, workspace) -> NuvemshopIntegration:
    """
    Orquestra a finalização da integração da Nuvemshop.
    """
    try:
        # 1. Usa nossa função de auth para trocar o código pelo token
        auth_data = exchange_code_for_token(code)
        access_token = auth_data.get('access_token')
        store_id = str(auth_data.get('user_id'))

        if not access_token or not store_id:
            raise NuvemshopAPIError("Resposta de autenticação da Nuvemshop está incompleta.")

        # 2. Gera nosso token secreto para os webhooks
        webhook_secret = f"nswh_{secrets.token_hex(24)}"

        # 3. Salva a integração
        integration_obj, created = NuvemshopIntegration.objects.update_or_create(
            store_id=store_id,
            defaults={
                'workspace': workspace,
                'access_token': access_token,
                'webhook_secret': webhook_secret,
                'is_active': True,
                'name': f"Loja Nuvemshop {store_id}"
            }
        )
        return integration_obj
    except NuvemshopAPIError as e:
        raise e # Propaga o erro para a view tratar

def handle_nuvemshop_webhook(request: HttpRequest, integration: NuvemshopIntegration) -> HttpResponse:
    """
    Processa um webhook validado da Nuvemshop.
    """
    try:
        event_type = request.headers.get('x-nuvemshop-event', 'unknown')
        payload = json.loads(request.body)

        # Agora o import funciona, pois o modelo existe no lugar certo
        WebhookEvent.objects.create(
            workspace=integration.workspace,
            source=Integration.Type.NUVEMSHOP, # Usando o enum do modelo pai
            event_type=event_type,
            payload=payload,
        )
        return create_response(success=True, message='Webhook processado com sucesso')
    except json.JSONDecodeError:
        return create_response(success=False, message='Payload JSON inválido', status_code=400)
    except Exception as e:
        return create_response(success=False, message=f'Erro interno no servidor', status_code=500)