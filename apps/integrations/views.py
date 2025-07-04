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