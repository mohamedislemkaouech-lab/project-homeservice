from django import forms
from .models import Reservation


class ReservationForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    address_display = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True, 'placeholder': 'Cliquez sur la carte pour sélectionner une adresse'}),
        required=False
    )
    
    class Meta:
        model = Reservation
        fields = ['date', 'time_slot', 'notes', 'address', 'latitude', 'longitude', 'address_display']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes supplémentaires...'}),
            'address': forms.HiddenInput(),
        }
