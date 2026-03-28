from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('prestataire', 'Prestataire'),
        ('admin', 'Administrateur'),
    )
    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'En cours'),
        ('approved', 'Validé'),
        ('rejected', 'Rejeté'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    identity_document = models.FileField(upload_to='identity_docs/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_client(self):
        return self.role == 'client'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_prestataire(self):
        return self.role == 'prestataire'

    def save(self, *args, **kwargs):
        # Automatically set role to 'admin' for superusers or staff if still 'client'
        if (self.is_superuser or self.is_staff) and self.role == 'client':
            self.role = 'admin'
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        from reviews.models import Review
        reviews = Review.objects.filter(reservation__service__provider=self)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def detailed_ratings(self):
        from reviews.models import Review
        reviews = Review.objects.filter(reservation__service__provider=self)
        if reviews.exists():
            avg_data = reviews.aggregate(
                models.Avg('rating_punctuality'),
                models.Avg('rating_quality'),
                models.Avg('rating_communication'),
                models.Avg('rating_value')
            )
            return {
                'punctuality': round(avg_data['rating_punctuality__avg'] or 5, 1),
                'quality': round(avg_data['rating_quality__avg'] or 5, 1),
                'communication': round(avg_data['rating_communication__avg'] or 5, 1),
                'value': round(avg_data['rating_value__avg'] or 5, 1)
            }
        return {'punctuality': 0, 'quality': 0, 'communication': 0, 'value': 0}

    @property
    def total_reviews(self):
        from reviews.models import Review
        return Review.objects.filter(reservation__service__provider=self).count()
