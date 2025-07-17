from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

#from django.conf import settings
from django.contrib.auth.decorators import login_required

from common.utils.responses import create_response
from common.utils.redirects import redirect_with_message 
from common.exceptions import IntegrationError

from apps.integrations.messaging.whatsapp.models import WhatsappIntegration
from evolutionapi.models.instance import InstanceConfig
from apps.integrations.messaging.whatsapp.client._evolution_client import get_evolution_client
from .services import has_existing_integration, create_whatsapp_integration
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

    return create_response(success=True, message='teste ok', status_code=200)


@login_required(login_url='accounts:login')
def start_whatsapp_auth(request):
    if request.method != "POST":
        return create_response(success=False, message='Método não permitido', status_code=405)

    phone = request.POST.get('phone')

    exists = has_existing_integration(phone)
    if not exists:
        create_whatsapp_integration(phone)
        return redirect_with_message('integrations_ui:integrations', request, 'Integração sendo realizada', level='success')


    return redirect_with_message(
        'integrations_ui:integrations',
        request,
        f"teste - já existe integração? {exists}",
        level='success'
    )

