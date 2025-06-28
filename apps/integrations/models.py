# Em apps/integrations/models.py

from django.db import models
from core.model import BaseModel # Importamos nosso novo BaseModel

class Integration(BaseModel):
    """
    Modelo base para todas as integrações.
    Este modelo NÃO é abstrato. Ele guarda a informação comum
    e permite que busquemos todas as integrações de um workspace.
    """
    class Type(models.TextChoices):
        NUVEMSHOP = 'NUVEMSHOP'
        MERCADOLIVRE = 'MERCADOLIVRE'
        WHATSAPP = 'WHATSAPP'
        # ...

    integration_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        verbose_name='Tipo de Integração'
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativa')

    class Meta:
        verbose_name = 'Integração'
        verbose_name_plural = 'Integrações'

    def __str__(self):
        return f"{self.workspace.name} - {self.get_integration_type_display()}"