from django import forms
from django.db.models import Q
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

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')
        
        # Check if this form is for an existing reservation (edit mode)
        if hasattr(self, 'instance') and self.instance.pk:
            # Exclude current reservation from the check
            existing_reservations = Reservation.objects.filter(
                service=self.instance.service,
                date=date,
                time_slot=time_slot
            ).exclude(pk=self.instance.pk)
        else:
            # For new reservations, we need to get the service from the view
            # We'll handle this in the view for now
            return cleaned_data
        
        # Check for conflicts with pending or accepted reservations
        conflicts = existing_reservations.filter(
            status__in=['pending', 'accepted']
        )
        
        if conflicts.exists():
            raise forms.ValidationError(
                "Ce créneau est déjà réservé pour ce service. Veuillez choisir une autre date ou heure."
            )
        
        return cleaned_data
