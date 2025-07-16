import secrets
import uuid
from django.db import models
from apps.integrations.models import Integration

class WhatsappIntegration(Integration):
    """
    Integração com o WhatsApp. Herda de Integration.
    """
    phone_number = models.CharField(max_length=100, verbose_name='Número de Telefone', unique=True)
    access_token = models.CharField(max_length=255, blank=True, verbose_name='Token de Acesso')
    webhook_secret = models.CharField(max_length=255, unique=True, verbose_name='Token Secreto do Webhook', blank=True)
    
    def save(self, *args, **kwargs):
        self.integration_type = Integration.Type.WHATSAPP

        if not self.name:
            self.name = f"whatsapp_{uuid.uuid4().hex[:8]}"

        if not self.webhook_secret:
            self.webhook_secret = f"wpwh_{secrets.token_hex(24)}"

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Integração WhatsApp'
        verbose_name_plural = 'Integrações WhatsApp'
