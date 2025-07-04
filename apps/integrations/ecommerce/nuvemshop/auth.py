# Em apps/integrations/ecommerce/nuvemshop/auth.py
import requests
import logging
from django.conf import settings
from .exceptions import NuvemshopAPIError # Importa nossa exceção customizada

logger = logging.getLogger(__name__)

def exchange_code_for_token(code: str) -> dict:
    """
    Troca o código de autorização temporário por um access token permanente.
    (Baseado na sua lógica original)
    """
    url = "https://www.tiendanube.com/apps/authorize/token"
    data = {
        "client_id": settings.NUVEMSHOP_CLIENT_ID,
        "client_secret": settings.NUVEMSHOP_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status() # Lança exceção para erros HTTP (4xx, 5xx)
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro de HTTP ao autenticar na Nuvemshop: {e.response.text}")
        raise NuvemshopAPIError(f"Erro de autenticação: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Erro inesperado na autenticação: {e}")
        raise NuvemshopAPIError("Erro de comunicação com a Nuvemshop.")