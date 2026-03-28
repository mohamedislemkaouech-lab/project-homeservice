from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class ClientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Prénom'}
    ))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Nom'}
    ))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}
    ))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Téléphone'}
    ))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Ville'}
    ))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'city', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        if commit:
            user.save()
        return user


class PrestataireRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Prénom'}
    ))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Nom'}
    ))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}
    ))
    phone = forms.CharField(max_length=20, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Téléphone'}
    ))
    city = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Ville'}
    ))
    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Adresse'}
    ))
    bio = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Décrivez votre expérience...', 'rows': 4}
    ))
    identity_document = forms.FileField(required=True, label="Pièce d'identité (Obligatoire)", widget=forms.FileInput(
        attrs={'class': 'form-control', 'accept': 'image/*,.pdf'}
    ))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'city', 'address', 'bio', 'identity_document', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'prestataire'
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}
    ))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'address', 'bio', 'profile_image', 'identity_document']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'identity_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
