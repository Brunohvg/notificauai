# Em apps/workspaces/middleware/workspace.py
# (Usando o estilo moderno, sem MiddlewareMixin)

from ..services.workspaces_services import get_user_workspace
from ..exceptions import WorkspaceNotFound

class WorkspaceMiddleware:
    def __init__(self, get_response):
        """
        Este método é chamado uma única vez pelo Django na inicialização.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Este método é chamado para cada requisição e contém a sua lógica.
        """
        # A sua lógica, perfeitamente aplicada aqui:
        request.workspace = None
        user = getattr(request, 'user', None)
        
        if user and user.is_authenticated: # and not user.is_superuser
            try:
                request.workspace = get_user_workspace(user)
            except WorkspaceNotFound:
                # O workspace já é None, então não precisamos fazer nada aqui.
                pass

        # Continua o processamento da requisição
        response = self.get_response(request)

        return response