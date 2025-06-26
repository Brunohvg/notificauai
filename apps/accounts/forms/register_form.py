from django import forms
from django.contrib.auth.forms import UserCreationForm
from ..models import User

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label="Nome",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Digite seu nome",
            "id": "first_name",
            "required": True
        })
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Digite seu email",
            "id": "email",
            "required": True

        })
    )

    phone = forms.CharField(
        label="Telefone",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Digite seu telefone",
            "id": "id_telefone",
            "required": True
        })
    )



    class Meta:
        model = User
        fields = ['first_name', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajusta tamanho dos inputs de senha
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite sua senha',
            'id': 'password1',
            'required': True
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme sua senha',
            'id': 'password2',
            'required': True
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        user.company_name = self.cleaned_data.get('company_name', '')
        user.is_active = True  # Ativa o usuário por padrão
        user.is_staff = False  # Não é um superusuário
        user.is_superuser = False  # Não é um superusuário
        if commit:
            user.save()
        return user
