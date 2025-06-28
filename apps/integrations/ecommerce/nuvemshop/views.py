from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Importe sua função de resposta padronizada
from common.utils.responses import create_response
# Importe o serviço e o modelo
from .services import handle_nuvemshop_webhook
from .models import NuvemshopIntegration

@csrf_exempt
def nuvemshop_webhook_receiver(request: HttpRequest) -> HttpResponse:
    """
    Recebe, autentica e delega o processamento de webhooks da Nuvemshop.
    """
    if request.method != 'POST':
        # Usando sua função!
        return create_response(success=False, message='Método não permitido', status_code=405)

    received_token = request.GET.get('token')
    if not received_token:
        # Usando sua função!
        return create_response(success=False, message='Token de autenticação não fornecido', status_code=401)

    try:
        integration = NuvemshopIntegration.objects.get(webhook_secret=received_token)
    except NuvemshopIntegration.DoesNotExist:
        # Usando sua função!
        return create_response(success=False, message='Integração não encontrada ou token inválido', status_code=404)

    # A delegação para o serviço continua a mesma
    return handle_nuvemshop_webhook(request, integration)