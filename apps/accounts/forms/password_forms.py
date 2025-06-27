# Em apps/accounts/forms/password_forms.py
from django import forms
# Importe o SetPasswordForm original do Django
from django.contrib.auth.forms import SetPasswordForm
# Importe o PasswordChangeForm original do Django
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
class SetNewPasswordForm(SetPasswordForm):
    # Sobrescrevemos os campos do formulário pai para adicionar nossos estilos.
    # É CRUCIAL usar os nomes new_password1 e new_password2.
    new_password1 = forms.CharField(
        label="Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control", # Seu estilo personalizado
            "placeholder": "Digite sua nova senha",
            "id": "id_new_password1"
        }),
    )

    new_password2 = forms.CharField(
        label="Confirmar Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control", # Seu estilo personalizado
            "placeholder": "Confirme sua nova senha",
            "id": "id_new_password2"
        }),
    )

    # O método clean() que valida se as senhas são iguais não é mais necessário,
    # pois a classe pai SetPasswordForm já faz isso.
    # O método save() também é herdado e já sabe como salvar a nova senha.
    # Não precisamos mais do método clean(), pois o SetPasswordForm já faz
    # a verificação de senhas iguais e a validação de força.
# -----------------------------------------------------------------------------
# Formulário para solicitar o reset de senha — usuário informa o email
# para receber o link de redefinição.
# -----------------------------------------------------------------------------
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Digite seu email",
            "id": "email"
        }),
        error_messages={
            'required': 'Este campo é obrigatório.',
            'invalid': 'Digite um email válido.'
        }
    )


# -----------------------------------------------------------------------------
# Formulário para o usuário trocar a própria senha (precisa estar logado).
# -----------------------------------------------------------------------------
# Damos um apelido ao import para evitar conflito de nome.
class PasswordChangeForm(DjangoPasswordChangeForm):
    # Sobrescrevemos os campos para aplicar nossos estilos
    old_password = forms.CharField(
        label="Senha Atual",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua senha atual",
            "id": "id_old_password"
        }),
    )

    new_password1 = forms.CharField(
        label="Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua nova senha",
            "id": "id_new_password1"
        }),
    )

    new_password2 = forms.CharField(
        label="Confirmar Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirme sua nova senha",
            "id": "id_new_password2"
        }),
    )

    # Não precisamos mais dos métodos __init__, clean() ou validate_password_strength().
    # A classe pai DjangoPasswordChangeForm já faz tudo isso:
    # 1. Valida se a 'old_password' está correta.
    # 2. Valida a força da 'new_password1' com base nas configurações do projeto.
    # 3. Valida se 'new_password1' e 'new_password2' são iguais.
    # 4. Fornece um método .save() que atualiza a senha do usuário.