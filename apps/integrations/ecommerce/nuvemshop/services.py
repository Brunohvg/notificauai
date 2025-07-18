import secrets
import json
from django.http import HttpRequest, HttpResponse
from django.db import transaction
from django.utils import timezone
# Funções e modelos do nosso projeto
from common.utils.responses import create_response
from apps.integrations.models import WebhookEvent, Integration
from .models import NuvemshopIntegration
#from .get_token import exchange_code_for_token
from .exceptions import NuvemshopAPIError
from nuvemshop_client import NuvemshopClient 
from django.conf import settings
from apps.orders.services.order_service import create_order_from_webhook

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
        print(get_store_info(integration))
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
    print(get_store_info(integration))
    return integration


def create_nuvemshop_webhook(integration: NuvemshopIntegration, event_type: str) -> dict:
    """
    Cria um webhook na Nuvemshop e salva os dados na integração.
    """

    client = NuvemshopClient(
        store_id= int(integration.store_id),
        access_token=integration.access_token
    )
    webhook_url = f"{settings.BASE_URL}/api/v1/integrations/nuvemshop/webhook/{integration.webhook_secret}/"

    # webhook_url = f"{settings.BASE_URL}/apps/integrations/ecommerce/nuvemshop/webhooks/?token={integration.webhook_secret}"

    event_types = [
        "order/created",
        "order/updated",
        "order/paid",
        "order/packed",
        "order/fulfilled",
        "order/cancelled",
        "order/custom_fields_updated",
        "order/edited",
        "order/pending",
        "order/voided"
    ]

    try:
        # Evita duplicar webhooks: verifica se já foi criado
        if integration.webhook_url == webhook_url and integration.webhook_active:
            return {
                "message": "Webhook já existente e ativo.",
                "webhook_url": integration.webhook_url,
                "webhook_id": integration.webhook_id,
            }

        created_webhooks = []

        for event in event_types:
            webhook_data = {
                "event": event,
                "url": webhook_url
            }

            response = client.webhooks.create(data=webhook_data)
            created_webhooks.append({
                "event": event,
                "webhook_id": response.get("id"),
                "status": "criado"
            })

        return {
            "message": "Webhooks criados com sucesso.",
            "webhooks": created_webhooks
        }

    except Exception as e:
        print("Erro ao criar webhooks:", str(e))
        raise


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


def get_store_info(integration: NuvemshopIntegration) -> dict:
    """
    Obtém informações da loja Nuvemshop.
    """
    client = NuvemshopClient(
        store_id=integration.store_id,
        access_token=integration.access_token
    )
    
    try:
        store_info = client.stores.get()
        if not store_info:
            raise NuvemshopAPIError("Não foi possível obter informações da loja.")  
        # A Nuvemshop retorna uma lista, mas queremos o primeiro item
        integration.store_name = store_info.get("name", "").get("pt", '')
        integration.store_email = store_info.get("email", "")
        integration.store_phone = store_info.get("phone", "")
        integration.store_domain = store_info.get("original_domain", "")
        integration.store_document = store_info.get("business_id", "")     
        integration.save(update_fields=[
            'store_name',
            'store_email',
            'store_phone',
            'store_domain',
            'store_document'
        ])  
        # Retorna um dicionário com as informações da loja
        return store_info

    except Exception as e:
        raise NuvemshopAPIError(f"Erro ao obter informações da loja: {str(e)}")


def handle_nuvemshop_webhook(request: HttpRequest, integration: Integration) -> HttpResponse:
    try:
        payload = json.loads(request.body)
        event_type = payload.get('event', 'unknown')

        evento = WebhookEvent.objects.create(
            workspace=integration.workspace,
            source=Integration.Type.NUVEMSHOP,
            event_type=event_type,
            payload=payload,
        )

        # Tenta processar se for evento suportado
        try:
            create_order_from_webhook(webhook_event=evento, integration=integration)
        except NotImplementedError as e:
            # Evento reconhecido mas não tratado (ex: sem parser) — OK ignorar
            print(f"Ignorando evento: {e}")
        except Exception as e:
            # Outros erros de lógica — registra, mas não quebra o fluxo
            print(f"Erro ao processar webhook: {e}")

        return create_response(success=True, message="Webhook recebido e tratado (ou ignorado) com sucesso")

    except json.JSONDecodeError:
        return create_response(success=False, message='Payload JSON inválido', status_code=400)
    except Exception:
        return create_response(success=False, message='Erro interno no servidor', status_code=500)

