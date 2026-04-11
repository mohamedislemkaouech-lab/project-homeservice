from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from services.models import Service, Category
from .models import Reservation

class ReservationsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_user = User.objects.create_user(username='c_user', password='pw', role='client')
        self.provider = User.objects.create_user(username='p_user', password='pw', role='prestataire')
        self.category = Category.objects.create(name='Cat')
        self.service = Service.objects.create(
            provider=self.provider, category=self.category, title='Service 1',
            price=10.0, city='Paris', description='desc'
        )

    def test_create_reservation(self):
        self.client.force_login(self.client_user)
        response = self.client.post(reverse('create_reservation', args=[self.service.pk]), {
            'date': '2030-01-01',
            'time_slot': '10:00:00',
            'notes': 'Please be on time'
        })
        self.assertRedirects(response, reverse('my_reservations'))
        self.assertTrue(Reservation.objects.filter(service=self.service, client=self.client_user, status='pending').exists())

    def test_cancel_reservation(self):
        self.client.force_login(self.client_user)
        reservation = Reservation.objects.create(
            client=self.client_user, service=self.service, date='2030-01-01', time_slot='10:00:00', status='pending'
        )
        response = self.client.post(reverse('cancel_reservation', args=[reservation.pk]))
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'cancelled')

    def test_provider_accept_reject_flow(self):
        reservation = Reservation.objects.create(
            client=self.client_user, service=self.service, date='2030-01-01', time_slot='10:00:00', status='pending'
        )
        
        # Client tries to accept -> error/redirect
        self.client.force_login(self.client_user)
        response = self.client.get(reverse('update_reservation_status', args=[reservation.pk, 'accepted']))
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'pending')

        # Provider accepts
        self.client.force_login(self.provider)
        response = self.client.get(reverse('update_reservation_status', args=[reservation.pk, 'accepted']))
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'accepted')
