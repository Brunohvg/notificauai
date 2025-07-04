from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from django.conf import settings
from django.contrib.auth.decorators import login_required
from common.utils.redirects import redirect_with_message

# Importe o serviço que acabamos de criar
from .services import finalize_nuvemshop_integration
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





@login_required(login_url='accounts:login')
def start_nuvemshop_auth(request):
    """
    View que inicia o fluxo OAuth.
    Redireciona o usuário para a página de autorização da Nuvemshop.
    """
    # Monta a URL de autorização da Nuvemshop
    auth_url = (
        f"https://www.nuvemshop.com.br/apps/{settings.NUVEMSHOP_CLIENT_ID}/authorize"
        f"?response_type=code"
        f"&scope=read_orders read_products" # Escopos que estamos a solicitar
    )
    return redirect(auth_url)


@login_required(login_url='accounts:login')
def nuvemshop_callback(request):
    """
    View que recebe o callback da Nuvemshop após a autorização do usuário.
    """
    code = request.GET.get('code')
    workspace = request.workspace # Usando o middleware!

    # A view apenas valida o básico e chama o serviço
    if not code:
        return redirect_with_message('integrations_ui:integrations_view', request, "Autorização falhou: código não fornecido.", level='error')

    if not workspace:
        return redirect_with_message('integrations_ui:integrations_view', request, "Workspace não encontrado. Por favor, tente novamente.", level='error')

    try:
        # A view delega TODO o trabalho pesado para o serviço
        integration = finalize_nuvemshop_integration(code=code, workspace=workspace)
        message = f"Integração com a loja '{integration.name}' realizada com sucesso!"
        return redirect_with_message('integrations_ui:integrations_view', request, message, level='success')

    except Exception as e:
        # Se o serviço levantar uma exceção, a view a captura e mostra uma mensagem de erro amigável.
        # Adicionar logs do erro 'e' aqui é crucial.
        message = f"Ocorreu um erro ao conectar com a Nuvemshop: {e}"
        return redirect_with_message('integrations_ui:integrations_view', request, message, level='error')