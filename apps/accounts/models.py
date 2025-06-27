# Em apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Endereço de e-mail',
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Nome',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Sobrenome',
        max_length=150,
        blank=True
    )
    phone = models.CharField(
        verbose_name='Telefone',
        max_length=20,
        blank=True
    )
    company_name = models.CharField(
        verbose_name='Nome da Empresa',
        max_length=200,
        blank=True
    )

    is_active = models.BooleanField(
        verbose_name='Usuário Ativo',
        default=True,
        help_text='Desmarque para desativar o usuário em vez de excluí-lo.'
    )
    is_staff = models.BooleanField(
        verbose_name='Membro da Equipe',
        default=False,
        help_text='Define se o usuário pode fazer login no site de administração.'
    )
    date_joined = models.DateTimeField(
        verbose_name='Data de Cadastro',
        default=timezone.now
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['email']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """ Retorna o nome completo do usuário. """
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuário'
    )
    bio = models.TextField(
        verbose_name='Biografia',
        blank=True
    )
    avatar = models.ImageField(
        verbose_name='Avatar',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    notification_email = models.BooleanField(
        verbose_name='Receber notificações por e-mail',
        default=True
    )
    notification_dashboard = models.BooleanField(
        verbose_name='Receber notificações no painel',
        default=True
    )
    
    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'

    def __str__(self):
        return f"Perfil de {self.user.email}"