from django import forms

# -----------------------------------------------------------------------------
# Formulário usado quando o usuário acessa o link de redefinição de senha
# (geralmente enviado por e-mail). Ele define uma nova senha sem precisar da atual.
# -----------------------------------------------------------------------------
class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua nova senha",
            "id": "new_password"
        }),
        error_messages={'required': 'Por favor, preencha a nova senha.'}
    )

    confirm_new_password = forms.CharField(
        label="Confirmar Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirme sua nova senha",
            "id": "confirm_new_password"
        }),
        error_messages={'required': 'Por favor, confirme a nova senha.'}
    )

    def clean(self):
        """
        Valida se as duas senhas digitadas são iguais.
        """
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data


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
# Formulário usado quando o usuário quer trocar a senha manualmente
# já estando logado. Requer senha atual, nova senha e confirmação.
# -----------------------------------------------------------------------------
class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label="Senha Atual",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua senha atual",
            "id": "old_password"
        }),
        error_messages={'required': 'Por favor, preencha a senha atual.'}
    )
    new_password = forms.CharField(
        label="Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua nova senha",
            "id": "new_password"
        }),
        error_messages={'required': 'Por favor, preencha a nova senha.'}
    )
    confirm_password = forms.CharField(
        label="Confirmar Nova Senha",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirme sua nova senha",
            "id": "confirm_password"
        }),
        error_messages={'required': 'Por favor, confirme a nova senha.'}
    )

    def __init__(self, user=None, *args, **kwargs):
        """
        Recebe o usuário logado para poder validar a senha atual.
        """
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        """
        Valida:
        - Se a senha atual está correta.
        - Se a nova senha é diferente da atual.
        - Se confirmação bate com a nova senha.
        - Se a nova senha é forte (usando função separada).
        """
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if old_password and not self.user.check_password(old_password):
            self.add_error('old_password', "Senha atual incorreta.")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "As novas senhas não coincidem.")

        if new_password and old_password and new_password == old_password:
            self.add_error('new_password', "A nova senha não pode ser igual à senha atual.")

        # Validação de força da senha (chama método separado)
        if new_password:
            self.validate_password_strength(new_password)

        return cleaned_data

    def validate_password_strength(self, password):
        """
        Regras básicas para força da senha:
        - Pelo menos 8 caracteres
        - Pelo menos 1 número
        - Pelo menos 1 letra
        - Pelo menos 1 caractere especial
        """
        if len(password) < 8:
            self.add_error('new_password', "A nova senha deve ter pelo menos 8 caracteres.")
        if not any(char.isdigit() for char in password):
            self.add_error('new_password', "A nova senha deve conter pelo menos um número.")
        if not any(char.isalpha() for char in password):
            self.add_error('new_password', "A nova senha deve conter pelo menos uma letra.")
        if not any(char in "!@#$%^&*()-_=+[]{};:,.<>?/" for char in password):
            self.add_error('new_password', "A nova senha deve conter pelo menos um caractere especial.")
