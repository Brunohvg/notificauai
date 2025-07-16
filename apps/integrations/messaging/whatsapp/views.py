from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

#from django.conf import settings
from django.contrib.auth.decorators import login_required
#from common.utils.redirects import redirect_with_message
from common.utils.responses import create_response
from common.exceptions import IntegrationError

from apps.integrations.messaging.whatsapp.models import WhatsappIntegration

from apps.integrations.messaging.whatsapp.services import handle_whatsapp_webhook

@csrf_exempt
def whatsapp_webhook_receiver(request: HttpRequest, received_token: str) -> HttpResponse:
    """
    Recebe, autentica e delega o processamento de webhooks da Nuvemshop.
    """
    if request.method != 'POST':
        return create_response(success=False, message='Método não permitido', status_code=405, data={'token': received_token})

    try:
        integration = WhatsappIntegration.objects.get(webhook_secret=received_token)
    except WhatsappIntegration.DoesNotExist:
        return create_response(success=False, message='Integração não encontrada ou token inválido', status_code=404)

    return handle_whatsapp_webhook(request=request, integration=integration)

