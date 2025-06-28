import json
from django.http import HttpRequest, HttpResponse

# Importe sua função de resposta padronizada
from common.utils.responses import create_response
# Importe os modelos necessários
from apps.integrations.models import WebhookEvent
from .models import NuvemshopIntegration

def handle_nuvemshop_webhook(request: HttpRequest, integration: NuvemshopIntegration) -> HttpResponse:
    """
    Processa um webhook validado da Nuvemshop.
    """
    try:
        event_type = request.headers.get('x-nuvemshop-event', 'unknown')
        payload = json.loads(request.body)

        WebhookEvent.objects.create(
            workspace=integration.workspace,
            source=WebhookEvent.Type.NUVEMSHOP,
            event_type=event_type,
            payload=payload,
        )

        # Usando sua função para a resposta de sucesso!
        return create_response(success=True, message='Webhook processado com sucesso', status_code=200)

    except json.JSONDecodeError:
        # Usando sua função!
        return create_response(success=False, message='Payload JSON inválido', status_code=400)
    except Exception as e:
        # Usando sua função!
        # No futuro, podemos adicionar o erro 'e' ao log aqui.
        return create_response(success=False, message='Erro interno no servidor', status_code=500)