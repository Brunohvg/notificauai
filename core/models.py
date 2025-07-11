# Em apps/core/models.py (ou um novo app common)

from django.db import models
from apps.workspaces.models import Workspace

class BaseModel(models.Model):
    """
    Um modelo base abstrato que fornece os campos
    `workspace`, `created_at`, e `updated_at`.
    """
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, verbose_name='Workspace')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        abstract = True