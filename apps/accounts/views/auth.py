import logging
from django.shortcuts import render
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from ..forms import (
    UserLoginForm,
    UserRegistrationForm,
    PasswordResetRequestForm,
    SetNewPasswordForm,
)
from ..services import (
    login_user,
    register_user,
    send_password_recovery_email,
)
from common.utils.messages import add_message
from common.utils.redirects import redirect_with_message

logger = logging.getLogger('accounts')
User = get_user_model()


def login_view(request):
    form = UserLoginForm(request.POST or None)

    if form.is_valid():
        email = form.cleaned_data['email']
        senha = form.cleaned_data['senha']
        user = login_user(email, senha)

        if user:
            auth_login(request, user)
            logger.info(f"Login bem-sucedido para o usuário: {email}")
            return redirect_with_message('integrations_ui:integrations', request, "Logado com sucesso.", level='success')

        logger.warning(f"Tentativa de login inválida para o email: {email}")
        add_message(request, "Email ou senha incorretos.", level='error', extra_tags='danger')

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    form = UserRegistrationForm(request.POST or None)

    if form.is_valid():
        user = register_user(form)
        logger.info(f"Novo cadastro realizado: {user.email}")
        return redirect_with_message('accounts:login', request, "Cadastro realizado com sucesso.", level='success')

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logger.info(f"Logout realizado por: {request.user.email}")
    auth_logout(request)
    return redirect_with_message('accounts:login', request, "Você saiu da conta.", level='info')


def password_reset_request_view(request):
    form = PasswordResetRequestForm(request.POST or None)

    if form.is_valid():
        email = form.cleaned_data['email']
        if send_password_recovery_email(email, request):
            logger.info(f"Solicitação de recuperação de senha enviada para: {email}")
            return render(request, 'accounts/email_sent.html')

        logger.warning(f"Tentativa de recuperação com email não cadastrado: {email}")
        form.add_error('email', 'Email não cadastrado.')

    return render(request, 'accounts/password_reset.html', {'form': form})


def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception as e:
        logger.error(f"Erro ao decodificar UID ou recuperar usuário: {e}")
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        logger.warning("Token inválido ou expirado na redefinição de senha.")
        return redirect_with_message(
            'accounts:login', request,
            "Link de redefinição de senha inválido ou expirado.",
            level='error', extra_tags='danger'
        )

    if request.method == 'POST':
        form = SetNewPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            logger.info(f"Senha redefinida com sucesso para: {user.email}")
            return redirect_with_message('accounts:login', request, "Sua senha foi redefinida com sucesso.", level='success')
    else:
        form = SetNewPasswordForm(user)

    return render(request, 'accounts/password_reset_confirm.html', {'form': form})
