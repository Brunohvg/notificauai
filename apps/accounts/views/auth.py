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

User = get_user_model()

def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        user = login_user(form.cleaned_data['email'], form.cleaned_data['senha'])
        if user:
            auth_login(request, user)
            return redirect_with_message('accounts:perfil', request, "Logado com sucesso.", level='success')
        add_message(request, "Email ou senha incorretos.", level='error', extra_tags='danger')
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        register_user(form)
        return redirect_with_message('accounts:login', request, "Cadastro realizado com sucesso.", level='success')
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    return redirect_with_message('accounts:login', request, "Você saiu da conta.", level='info')


# -----------------------------------------------------------------------------
# View para o usuário solicitar redefinição de senha (email de recuperação).
# -----------------------------------------------------------------------------
def password_reset_request_view(request):
    form = PasswordResetRequestForm(request.POST or None)
    if form.is_valid():
        if send_password_recovery_email(form.cleaned_data['email'], request):
            
            return render(request, 'accounts/email_sent.html')
        form.add_error('email', 'Email não cadastrado.')
    return render(request, 'accounts/password_reset.html', {'form': form})


# -----------------------------------------------------------------------------
# View que o usuário acessa ao clicar no link do email de redefinição.
# Permite definir uma nova senha.
# -----------------------------------------------------------------------------

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return redirect_with_message('accounts:login', request, "Link de redefinição de senha inválido ou expirado.", level='error', extra_tags='danger')

    if request.method == 'POST':
        # Instanciamos o SEU formulário, que agora é mais inteligente
        form = SetNewPasswordForm(user, request.POST)
        if form.is_valid():
            # AQUI ESTÁ A CORREÇÃO:
            # Chamamos o método .save() que ele herdou do SetPasswordForm.
            # Isso corrige o KeyError e salva a senha corretamente.
            form.save()
            return redirect_with_message('accounts:login', request, "Sua senha foi redefinida com sucesso.", level='success')
    else:
        form = SetNewPasswordForm(user)

    return render(request, 'accounts/password_reset_confirm.html', {'form': form})