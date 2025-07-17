from .models import WhatsappIntegration
from common.utils.responses import create_response 
from .client._evolution_client import get_evolution_client
from evolutionapi.models.instance import InstanceConfig
import uuid


def has_existing_integration(phone) -> bool:
    """
    Verifica se já existe uma integração com o número de telefone informado.
    Retorna True se existir, False caso contrário.
    """
    return WhatsappIntegration.objects.filter(phone_number=phone).exists()


def create_whatsapp_integration(phone):
    client = get_evolution_client()
    name = f"whatsapp_{uuid.uuid4().hex[:8]}"
    # Configuração completa
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
    print(new_instance)
    return new_instance
