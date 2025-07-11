# Em apps/integrations/models.py

from django.db import models
from core.models import BaseModel # Ou de onde você importa seu BaseModel
from apps.workspaces.models import Workspace

# --- Modelo Base de Integração (já estava correto) ---
class Integration(BaseModel):
    class Type(models.TextChoices):
        NUVEMSHOP = 'NUVEMSHOP'
        MERCADOLIVRE = 'MERCADOLIVRE'
        WHATSAPP = 'WHATSAPP'
    
    integration_type = models.CharField(max_length=20, choices=Type.choices, verbose_name='Tipo de Integração')
    is_active = models.BooleanField(default=True, verbose_name='Ativa')
    name = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Integração'
        verbose_name_plural = 'Integrações'

    def __str__(self):
        return f"{self.workspace.name} - {self.get_integration_type_display()}"


# --- Modelo WebhookEvent (ADICIONE ESTE CÓDIGO) ---
class WebhookEvent(models.Model):
    """
    Armazena um evento de webhook recebido de uma plataforma externa.
    """
    STATUS_RECEIVED = 'received'
    STATUS_PROCESSED = 'processed'
    STATUS_ERROR = 'error'
    STATUS_CHOICES = [
        (STATUS_RECEIVED, 'Recebido'),
        (STATUS_PROCESSED, 'Processado'),
        (STATUS_ERROR, 'Erro'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='webhook_events')
    source = models.CharField(max_length=50, verbose_name='Fonte do Evento')
    event_type = models.CharField(max_length=100, verbose_name='Tipo do Evento')
    payload = models.JSONField(verbose_name='Payload do Evento')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
    error_message = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True, verbose_name='Recebido em')

    class Meta:
        verbose_name = 'Evento de Webhook'
        verbose_name_plural = 'Eventos de Webhook'
        ordering = ['-received_at']

    def __str__(self):
        return f"Evento de {self.source} ({self.event_type}) para {self.workspace.name}"