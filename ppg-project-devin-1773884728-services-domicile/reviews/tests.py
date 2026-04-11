from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from services.models import Service, Category
from reservations.models import Reservation
from .models import Review

class ReviewsViewTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(username='c_user', password='pw', role='client')
        self.provider = User.objects.create_user(username='p_user', password='pw', role='prestataire')
        self.category = Category.objects.create(name='Cat')
        self.service = Service.objects.create(
            provider=self.provider, category=self.category, title='Service 1',
            price=10.0, city='Paris', description='desc'
        )
        self.client = Client()

    def test_review_only_completed_reservation(self):
        self.client.force_login(self.client_user)
        # Pending reservation
        reservation = Reservation.objects.create(
            client=self.client_user, service=self.service, date='2030-01-01', time_slot='10:00:00', status='pending'
        )
        url = reverse('create_review', args=[reservation.pk])
        response = self.client.post(url, {
            'rating_punctuality': 5, 'rating_quality': 5, 'rating_communication': 5, 'rating_value': 5
        })
        # Should redirect back or show error
        self.assertRedirects(response, reverse('my_reservations'))
        self.assertFalse(Review.objects.filter(reservation=reservation).exists())

        # Complete the reservation
        reservation.status = 'completed'
        reservation.save()
        
        response = self.client.post(url, {
            'rating_punctuality': 5, 'rating_quality': 5, 'rating_communication': 5, 'rating_value': 5, 'comment': 'Top'
        })
        self.assertRedirects(response, reverse('my_reservations'))
        self.assertTrue(Review.objects.filter(reservation=reservation).exists())

    def test_cannot_review_twice(self):
        self.client.force_login(self.client_user)
        reservation = Reservation.objects.create(
            client=self.client_user, service=self.service, date='2030-01-01', time_slot='10:00:00', status='completed'
        )
        Review.objects.create(
            client=self.client_user, reservation=reservation,
            rating_punctuality=5, rating_quality=5, rating_communication=5, rating_value=5, rating=5
        )
        
        url = reverse('create_review', args=[reservation.pk])
        response = self.client.post(url, {
            'rating_punctuality': 1, 'rating_quality': 1, 'rating_communication': 1, 'rating_value': 1
        })
        self.assertRedirects(response, reverse('my_reservations'))
        # Ensure there is still only 1 review
        self.assertEqual(Review.objects.filter(reservation=reservation).count(), 1)
