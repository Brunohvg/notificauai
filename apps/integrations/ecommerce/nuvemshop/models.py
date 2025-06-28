# Em apps/integrations/ecommerce/nuvemshop/models.py

from django.db import models
from apps.integrations.models import Integration # Importamos o modelo base

class NuvemshopIntegration(Integration):
    """
    Modelo específico para a integração com a Nuvemshop.
    """
    # A herança multi-tabelas do Django cria uma relação OneToOne automaticamente
    # para o modelo 'Integration' pai.

    store_id = models.CharField(
        max_length=100,
        unique=True, # Garante que uma loja não pode ser integrada duas vezes
        verbose_name='ID da Loja Nuvemshop'
    )
    access_token = models.CharField(max_length=255, verbose_name='Token de Acesso')
    # Adicionamos o nosso token secreto para validar webhooks
    webhook_secret = models.CharField(max_length=255, unique=True)
    
    # Podemos adicionar outros campos específicos da Nuvemshop aqui no futuro.

    def save(self, *args, **kwargs):
        # Garantimos que o tipo da integração pai seja sempre NUVEMSHOP
        self.integration_type = Integration.Type.NUVEMSHOP
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Integração Nuvemshop'
        verbose_name_plural = 'Integrações Nuvemshop'