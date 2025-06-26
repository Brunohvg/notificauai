from django import forms
from ..models import User

class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nome",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Digite seu nome",
            "id": "first_name"
        })
    )

    phone = forms.CharField(
        label="Telefone",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Digite seu telefone",
            "id": "phone"
        })
    )
    
    document = forms.CharField(
        label="Documento",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Digite o número do documento",
            "id": "document"
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'phone', 'document']
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email",
                "readonly": True,  # Não deixa editar o email
            }),
        }

    # Método de validação do campo 'first_name'
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError('O nome é obrigatório!')
        return first_name

    def save(self, commit=True):
        # Recupera o usuário atual
        user = super().save(commit=False)
        
        # Ajusta os valores dos campos conforme necessário
        user.first_name = self.cleaned_data['first_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.company_name = self.cleaned_data.get('company_name', '')
        user.document = self.cleaned_data.get('document', '')

        if commit:
            user.save()

        return user

