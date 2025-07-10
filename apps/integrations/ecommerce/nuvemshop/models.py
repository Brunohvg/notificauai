# Em apps/integrations/ecommerce/nuvemshop/models.py

from django.db import models
from apps.integrations.models import Integration # Importamos o modelo base

class NuvemshopIntegration(Integration):
    """
    Modelo específico para a integração com a Nuvemshop.
    """
    # A herança multi-tabelas do Django cria uma relação OneToOne automaticamente
    # para o modelo 'Integration' pai.
    #Garante que uma loja não pode ser integrada duas vezes

    store_id = models.IntegerField(unique=True, verbose_name='ID da Loja Nuvemshop')
    access_token = models.CharField(max_length=255, verbose_name='Token de Acesso')
    
    # Adicionamos o nosso token secreto para validar webhooks
    webhook_secret = models.CharField(max_length=255, unique=True)
    webhook_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID do Webhook')
    webhook_created_at = models.DateTimeField(blank=True, null=True, verbose_name='Data de Criação do Webhook')
    webhook_active = models.BooleanField(default=True, verbose_name='Webhook Ativo')
    webhook_url = models.URLField(blank=True, null=True, verbose_name='URL do Webhook')

    # Podemos adicionar outros campos específicos da Nuvemshop aqui no futuro.
    store_name = models.CharField(max_length=255, blank=True, verbose_name='Nome da Loja')
    store_phone = models.CharField(max_length=20, blank=True, verbose_name='Número de Telefone')
    store_email = models.EmailField(blank=True, verbose_name='Email da Loja')
    store_domain = models.CharField(max_length=255, blank=True, verbose_name='Domínio da Loja')
    store_document = models.CharField(max_length=20, blank=True, verbose_name='CPF/CNPJ da Loja')

        
    def save(self, *args, **kwargs):
        # Garantimos que o tipo da integração pai seja sempre NUVEMSHOP
        self.integration_type = Integration.Type.NUVEMSHOP
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Integração Nuvemshop'
        verbose_name_plural = 'Integrações Nuvemshop'


