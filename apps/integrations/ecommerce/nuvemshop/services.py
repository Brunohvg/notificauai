import secrets
import json
from django.http import HttpRequest, HttpResponse
from django.db import transaction
from django.utils import timezone
# Funções e modelos do nosso projeto
from common.utils.responses import create_response
from apps.integrations.models import WebhookEvent, Integration
from .models import NuvemshopIntegration
from .auth import exchange_code_for_token
from .exceptions import NuvemshopAPIError
from nuvemshop_client import NuvemshopClient 
from django.conf import settings

def finalize_nuvemshop_integration(code: str, workspace) -> NuvemshopIntegration:
    """
    Finaliza a integração com a Nuvemshop.
    Atualiza o token no dono original da loja mesmo que outro workspace tente integrar.
    """

    # 1. Troca o código por um access token
    auth_data = NuvemshopClient.authenticate(
        client_id=settings.NUVEMSHOP_CLIENT_ID,
        client_secret=settings.NUVEMSHOP_CLIENT_SECRET,
        code=code
    )

    access_token = auth_data.get('access_token')
    store_id = str(auth_data.get('user_id'))

    if not access_token or not store_id:
        raise NuvemshopAPIError("Resposta de autenticação da Nuvemshop está incompleta.")

    # 2. Busca a integração existente
    integration = NuvemshopIntegration.objects.filter(store_id=store_id).first()

    if integration:
        if integration.workspace != workspace:
            # Atualiza o token fora de transação
            NuvemshopIntegration.objects.filter(pk=integration.pk).update(
                access_token=access_token,
                is_active=True
            )
            raise NuvemshopAPIError("Esta loja já está integrada com outro usuário.")

        # Dono correto: atualiza normalmente
        integration.access_token = access_token
        integration.is_active = True
        integration.save(update_fields=['access_token', 'is_active'])

        # Garante que o webhook está presente
        create_nuvemshop_webhook(integration, event_type="order/create")
        return integration

    # 3. Loja nova: cria com segurança
    webhook_secret = f"nswh_{secrets.token_hex(24)}"

    with transaction.atomic():
        integration = NuvemshopIntegration.objects.create(
            store_id=store_id,
            workspace=workspace,
            access_token=access_token,
            webhook_secret=webhook_secret,
            is_active=True,
            name=f"Loja Nuvemshop {store_id}"
        )

    # Cria o webhook DEPOIS de garantir que a integração foi salva
    create_nuvemshop_webhook(integration, event_type="order/create")
    return integration



def create_nuvemshop_webhook(integration: NuvemshopIntegration, event_type: str) -> dict:
    """
    Cria um webhook na Nuvemshop e salva os dados na integração.
    """

    client = NuvemshopClient(
        store_id=integration.store_id,
        access_token=integration.access_token
    )
    webhook_url = f"{settings.BASE_URL}/api/v1/integrations/nuvemshop/webhook/{integration.webhook_secret}/"

    #webhook_url = f"{settings.BASE_URL}/apps/integrations/ecommerce/nuvemshop/webhooks/?token={integration.webhook_secret}"
    event_type = "product/created"
    try:
        # Evita duplicar webhooks: verifica se já foi criado
        if integration.webhook_url == webhook_url and integration.webhook_active:
            return {
                "message": "Webhook já existente e ativo.",
                "webhook_url": integration.webhook_url,
                "webhook_id": integration.webhook_id,
            }

        webhook_data = {
            "event": event_type,
            "url": webhook_url
        }

        response = client.webhooks.create(data=webhook_data)

        # Salva os dados do webhook criado
        integration.webhook_url = webhook_url
        integration.webhook_id = response.get("id")
        integration.webhook_created_at = timezone.now()
        integration.webhook_active = True
        integration.save(update_fields=[
            'webhook_url',
            'webhook_id',
            'webhook_created_at',
            'webhook_active'
        ])

        return response

    except Exception as e:
        raise NuvemshopAPIError(f"Erro ao criar webhook: {str(e)}")

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
    


