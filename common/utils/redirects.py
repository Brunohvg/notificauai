from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponseRedirect
from common.utils.messages import add_message
from typing import Literal

def redirect_with_message(
    url_name: str,
    request: HttpRequest,
    msg: str,
    level: Literal['success', 'error', 'info', 'warning'] = 'success', extra_tags=None) -> HttpResponseRedirect:
    """
    Redireciona com uma mensagem do Django messages.

    Args:
        url_name (str): Nome da URL para redirecionar (pode ser reversível com 'redirect')
        request (HttpRequest): Requisição atual
        msg (str): Mensagem a ser exibida
        level (str): Nível da mensagem ('success', 'error', 'info', 'warning')

    Returns:
        HttpResponseRedirect
    """
    add_message(request, msg, level, extra_tags)
    return redirect(url_name)
