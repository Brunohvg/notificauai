from django.contrib.auth import authenticate, get_user_model
from ..utils import send_password_reset_email  # Corrigido: import da função real

User = get_user_model()


# -----------------------------------------------------------------------------
# Autentica o usuário com email e senha (via authenticate do Django)
# -----------------------------------------------------------------------------
def login_user(email, password):
    user = authenticate(username=email, password=password)
    return user


# -----------------------------------------------------------------------------
# Recebe um form já validado e salva o novo usuário
# -----------------------------------------------------------------------------
def register_user(form):
    return form.save()


# -----------------------------------------------------------------------------
# Envia o email com link de redefinição de senha (caso o usuário exista)
# -----------------------------------------------------------------------------
def send_password_recovery_email(email, request):
    try:
        user = User.objects.get(email=email)
        send_password_reset_email(user, request)  # chamada real da função de envio
        return True
    except User.DoesNotExist:
        return False


# -----------------------------------------------------------------------------
# Define nova senha para o usuário e salva
# -----------------------------------------------------------------------------
def reset_user_password(user, new_password):
    user.set_password(new_password)
    user.save()
