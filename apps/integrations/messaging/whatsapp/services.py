from .models import WhatsappIntegration
from common.utils.responses import create_response 
from .client._evolution_client import get_evolution_client
from evolutionapi.models.instance import InstanceConfig
from .parsers import WhatsappParser
import uuid
from evolutionapi.models.instance import WebhookConfig

def has_existing_integration(phone) -> bool:
    """
    Verifica se já existe uma integração com o número de telefone informado.
    Retorna True se existir, False caso contrário.
    """
    return WhatsappIntegration.objects.filter(phone_number=phone).exists()





def create_whatsapp_integration(phone, workspace):
    print(phone)
    print(workspace)

    client = get_evolution_client()
    name = f"whatsapp_{uuid.uuid4().hex[:8]}"
    
    config = InstanceConfig(
        instanceName=name,
        integration="WHATSAPP-BAILEYS",
        number=f"55{phone}",
        qrcode=True,
        rejectCall=True,
        msgCall="Não Aceitamos ligações",
        groupsIgnore=True,
        alwaysOnline=True,
        readMessages=True,
        readStatus=True,
        syncFullHistory=True
    )

    new_instance = client.instances.create_instance(config)

    parser = WhatsappParser(payload=new_instance)
    parsed_data = parser.parse()

    print(parsed_data.get('access_token'))  # corrigido

    instancia, created = WhatsappIntegration.objects.update_or_create(
        phone_number=phone,
        workspace=workspace,  # certifique que existe esse campo no model
        defaults=parsed_data
    )

    return instancia


