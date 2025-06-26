"""
Serviços relacionados a workspaces e integrações
"""

from apps.integrations.models import Integration
from common.exceptions import IntegrationNotFound, WorkspaceNotFound

def get_user_workspace(user):
    """
    Busca o primeiro workspace do usuário
    
    Args:
        user: Usuário logado
        
    Returns:
        Workspace ou None se não existir
    """
    try:
        return user.workspaces.first()
    except WorkspaceNotFound:
        raise WorkspaceNotFound("Nenhum workspace encontrado para o usuário")
    except Exception as e:
        raise WorkspaceNotFound(f"Erro ao buscar workspace: {str(e)}")


def get_integration(workspace):
    """
    Busca a integração de WhatsApp ativa associada ao workspace.
    
    Args:
        workspace: Workspace do usuário
        
    Returns:
        Integration
    
    Raises:
        IntegrationNotFound: se nenhuma integração ativa for encontrada
    """
    try:
        return Integration.objects.get(
            workspace=workspace,
            integration_type=Integration.Type.WHATSAPP,
            is_active=True
        )
    except Integration.DoesNotExist:
        raise IntegrationNotFound("Integração WhatsApp ativa não encontrada para este workspace")

def workspace_has_integration(workspace):
    """
    Verifica se o workspace possui uma integração ativa de WhatsApp.

    Args:
        workspace: Workspace do usuário

    Returns:
        bool: True se houver uma integração ativa, False caso contrário
    """
    return Integration.objects.filter(
        workspace=workspace,
        integration_type=Integration.Type.WHATSAPP,
        is_active=True
    ).exists()