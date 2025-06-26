"""
Utilitários para mensagens do Django e respostas padrão
"""

from typing import Optional, Any, Literal
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpRequest


def add_message(
    request: HttpRequest,
    msg: str,
    level: Literal['success', 'error', 'info', 'warning'] = 'info',
    extra_tags: Optional[str] = None
) -> None:
    """
    Adiciona uma mensagem genérica ao request.

    Args:
        request (HttpRequest): Objeto da requisição
        msg (str): Mensagem a ser exibida
        level (str): Nível da mensagem
        extra_tags (str, opcional): Tags adicionais para estilização
    """
    level_func = {
        'success': messages.success,
        'error': messages.error,
        'info': messages.info,
        'warning': messages.warning,
    }.get(level, messages.info)

    level_func(request, msg, extra_tags=extra_tags)


def create_response(
    success: bool = True,
    message: str = "",
    data: Optional[Any] = None,
    status_code: int = 200
) -> JsonResponse:
    """
    Cria uma resposta padronizada para a API/webhook.

    Args:
        success (bool): Se foi bem-sucedido
        message (str): Mensagem de retorno
        data (dict): Dados extras (opcional)
        status_code (int): Código HTTP

    Returns:
        JsonResponse
    """
    response_data = {
        'success': success,
        'message': message,
        'timestamp': timezone.now().isoformat()
    }

    if data is not None:
        response_data['data'] = data

    return JsonResponse(response_data, status=status_code)
