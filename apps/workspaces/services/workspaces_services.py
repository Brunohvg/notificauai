# Em apps/workspaces/services/workspace.py

# Importamos o modelo e a nossa nova exceção
from ..models import Workspace
from ..exceptions import WorkspaceNotFound

def get_user_workspace(user):
    """
    Busca o primeiro workspace ativo do usuário.
    """
    workspace = user.workspaces.first()
    if not workspace:
        raise WorkspaceNotFound("Nenhum workspace encontrado para o usuário.")
    return workspace

# No futuro, outras funções de serviço do workspace podem vir aqui...
# def add_user_to_workspace(user, workspace):
#     ...