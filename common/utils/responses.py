from django.utils import timezone
from typing import Any, Optional
from django.http import JsonResponse

def create_response(success: bool = True, message: str = "", data: Optional[Any] = None, status_code: int = 200) -> JsonResponse:
    """
    Cria uma resposta padronizada para APIs e webhooks.
    """
    payload = {
        "success": success,
        "message": message,
        #"timestamps": timezone.now().isoformat(),
        "timestamp": timezone.now().isoformat().replace('+00:00', 'Z')

    }

    if data is not None:
        payload["data"] = data

    return JsonResponse(payload, status=status_code)
