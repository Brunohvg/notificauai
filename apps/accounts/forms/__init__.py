# forms/__init__.py
# Importa todos os formulários para facilitar o acesso
from .register_form import UserRegistrationForm
from .login_form import UserLoginForm
from .password_forms import SetNewPasswordForm, PasswordChangeForm, PasswordResetRequestForm
from .profile_form import UserProfileUpdateForm
