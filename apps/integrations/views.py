from django.contrib.auth.decorators import login_required
from apps.integrations.models import Integration
from django.shortcuts import render

@login_required(login_url='accounts:login')
def integrations_view(request):
    """
    Lista todas as integrações do workspace ATIVO do usuário logado.
    """
    integrations = Integration.objects.filter(
        workspace=request.workspace
    )

    context = {
        'integrations': integrations,
        'workspace': request.workspace,
    }
    return render(request, 'integrations/integrations.html', context)




def integrations_delete(request, integration_id):
    """
    Exclui uma integração específica do workspace ATIVO do usuário logado.
    """
    try:
        integration = Integration.objects.get(id=integration_id, workspace=request.workspace)
        integration.delete()
        return render(request, 'integrations/integrations.html', {'message': 'Integração excluída com sucesso.'})
    except Integration.DoesNotExist:
        return render(request, 'integrations/integrations.html', {'error': 'Integração não encontrada.'})
    

    