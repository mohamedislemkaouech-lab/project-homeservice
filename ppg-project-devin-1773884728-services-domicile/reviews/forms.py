from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating_punctuality', 'rating_quality', 'rating_communication', 'rating_value', 'comment']
        widgets = {
            'rating_punctuality': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'rating_quality': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'rating_communication': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'rating_value': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Ajoutez un commentaire détaillé...'}),
        }
        labels = {
            'rating_punctuality': 'Ponctualité (1-5)',
            'rating_quality': 'Qualité du travail (1-5)',
            'rating_communication': 'Communication & Relationnel (1-5)',
            'rating_value': 'Rapport Qualité/Prix (1-5)',
            'comment': 'Votre commentaire'
        }
