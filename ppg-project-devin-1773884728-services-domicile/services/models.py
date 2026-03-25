from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='services',
        limit_choices_to={'role': 'prestataire'}
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_unit = models.CharField(
        max_length=20,
        choices=[('heure', 'Par heure'), ('service', 'Par service'), ('jour', 'Par jour')],
        default='heure'
    )
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.provider.get_full_name()}"

    @property
    def average_rating(self):
        from reviews.models import Review
        reviews = Review.objects.filter(reservation__service=self)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def total_reviews(self):
        from reviews.models import Review
        return Review.objects.filter(reservation__service=self).count()


class Availability(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Lundi'), (1, 'Mardi'), (2, 'Mercredi'),
        (3, 'Jeudi'), (4, 'Vendredi'), (5, 'Samedi'), (6, 'Dimanche'),
    ]
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Availabilities"
        ordering = ['day_of_week', 'start_time']
        unique_together = ['provider', 'day_of_week', 'start_time']

    def __str__(self):
        return f"{self.provider.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
