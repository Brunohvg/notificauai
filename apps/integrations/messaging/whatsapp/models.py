import secrets
import uuid
from django.db import models
from apps.integrations.models import Integration

class WhatsappIntegration(Integration):
    """
    Integração com o WhatsApp. Herda de Integration.
    Campos mapeados a partir do parser.
    """
    phone_number = models.CharField(
        max_length=100,
        verbose_name='Número de Telefone',
        unique=True
    )

    # Dados da instância
    instance_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID da Instância'
    )
    instance_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nome da Instância'
    )
    integration = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tipo de Integração'
    )
    status = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Status da Instância'
    )
    webhook_wa_business = models.TextField(
        blank=True,
        null=True,
        verbose_name='Webhook WA Business'
    )
    access_token_wa_business = models.TextField(
        blank=True,
        null=True,
        verbose_name='Access Token WA Business'
    )

    # QR Code
    qrcode_pairing_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Pairing Code'
    )
    qrcode_code = models.TextField(
        blank=True,
        verbose_name='Código QR'
    )
    qrcode_base64 = models.TextField(
        blank=True,
        verbose_name='QR Code em Base64'
    )

    # Autenticação geral
    access_token = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Token de Acesso'
    )
    webhook_secret = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='Token Secreto do Webhook'
    )

    def save(self, *args, **kwargs):
        self.integration_type = Integration.Type.WHATSAPP

        if not self.instance_name:
            self.instance_name = f"whatsapp_{uuid.uuid4().hex[:8]}"

        if not self.webhook_secret:
            self.webhook_secret = f"wpwh_{secrets.token_hex(24)}"

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Integração WhatsApp'
        verbose_name_plural = 'Integrações WhatsApp'
