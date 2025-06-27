# Em apps/workspaces/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify # Importamos o slugify

class Workspace(models.Model):
    """
    Representa um espaço de trabalho ou uma loja (tenant) no sistema.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workspaces',
        verbose_name='Proprietário',
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nome do Workspace'
    )
    # Sugestão: Adicionar um slug para URLs amigáveis
    slug = models.SlugField(
        max_length=120,
        unique=True, # Garante que não haverá dois slugs iguais em todo o sistema
        blank=True,
        verbose_name='Slug'
    )
    # Sugestão: Descomentar campos que serão úteis para integrações
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefone')
    document = models.CharField(max_length=20, blank=True, verbose_name='CNPJ/CPF')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Espaço de Trabalho'
        verbose_name_plural = 'Espaços de Trabalho'
        ordering = ['name']
        # Usamos a forma moderna de definir a restrição de unicidade
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='unique_workspace_per_owner')
        ]

    def __str__(self):
        return self.name or f"Workspace de {self.owner.username}"

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para gerar o slug automaticamente
        a partir do nome do workspace antes de salvar.
        """
        if not self.slug:
            # Cria um slug base a partir do nome
            base_slug = slugify(self.name)
            # Para garantir unicidade, podemos adicionar o ID do owner ou um timestamp
            # Aqui, para simplificar, vamos usar o nome e o ID do proprietário
            unique_slug = f"{base_slug}-{self.owner.id}"
            self.slug = unique_slug
        super().save(*args, **kwargs)