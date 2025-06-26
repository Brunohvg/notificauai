import logging
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

logger = logging.getLogger('usuarios')

# -----------------------------------------------------------------------------
# Envia email com link de redefinição de senha para o usuário.
# Esse link contém um token e o ID do usuário codificado em base64.
# -----------------------------------------------------------------------------
def send_password_reset_email(user, request):
    # Gera token seguro e codifica o ID do usuário
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Monta o link completo de redefinição de senha
    reset_link = request.build_absolute_uri(
        reverse('accounts:resetar_senha', args=[uid, token])
    )

    # Renderiza o HTML do email
    html_content = render_to_string('accounts/redefinir_senha_email.html', {
        'reset_url': reset_link,
        'client_name': user.first_name,
        'year': 2025,
    })

    # Monta e envia o email
    email = EmailMessage(
        subject='Redefinição de Senha',
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = 'html'
    email.send(fail_silently=False)

    # Loga o envio no sistema
    logger.info(f"E-mail de recuperação enviado para {user.email}")
