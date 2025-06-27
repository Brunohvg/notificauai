# O seu signal.py - Está corretíssimo!
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile
from apps.workspaces.models import Workspace

@receiver(post_save, sender=User)
def create_user_profile_and_workspace(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        # Esta linha está perfeita. Ela cria o Workspace com um nome padrão,
        # e o método .save() que definimos no modelo vai cuidar de gerar o slug.
        Workspace.objects.create(owner=instance, name=f"Workspace de {instance.first_name}")