from django import forms

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Digite seu email",
            "id": "email"
        })
    )
    senha = forms.CharField(
        label="Senha", 
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Digite sua senha",
            "id": "password"
        })
    )

