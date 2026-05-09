from django.db import models
from django.conf import settings
from django.db.models import Q

 

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_reservations'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    date = models.DateField()
    time_slot = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'date', 'time_slot'],
                condition=Q(status__in=['pending', 'accepted']),
                name='unique_active_reservation',
                violation_error_message='Ce créneau est déjà réservé pour ce service. Veuillez choisir une autre date ou heure.'
            )
        ]

    def __str__(self):
        return f"Réservation #{self.pk} - {self.client.get_full_name()} -> {self.service.title}"
