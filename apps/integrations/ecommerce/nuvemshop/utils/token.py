from apps.integrations.ecommerce.nuvemshop.models import NuvemshopIntegration

def get_nuvemshop_credentials(workspace):
    try:
        integration = NuvemshopIntegration.objects.get(workspace=workspace)

        if not integration.access_token or not integration.store_id:
            raise ValueError("Access token ou store ID ausente na integração Nuvemshop.")

        return {
            "access_token": integration.access_token,
            "store_id": integration.store_id
        }

    except NuvemshopIntegration.DoesNotExist:
        raise ValueError("Integração Nuvemshop não encontrada para esse workspace.")
