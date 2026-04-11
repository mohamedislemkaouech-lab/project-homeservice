from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from .models import Service, Category

class ServicesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.provider = User.objects.create_user(
            username='prov1', password='pw', role='prestataire'
        )
        self.client_user = User.objects.create_user(
            username='c_user', password='pw', role='client'
        )
        self.category = Category.objects.create(name='Plomberie', description='Plumbing services')
        self.service1 = Service.objects.create(
            provider=self.provider, category=self.category, title='Réparation Fuite',
            description='je répare', price=50.00, city='Paris', is_active=True
        )
        self.service2 = Service.objects.create(
            provider=self.provider, category=self.category, title='Installation',
            description='j\'installe', price=150.00, city='Lyon', is_active=True
        )

    def test_service_creation_provider_only(self):
        url = reverse('service_create')
        
        # Test client cannot create
        self.client.force_login(self.client_user)
        response = self.client.post(url, {'title': 'T', 'category': self.category.pk, 'price': 10, 'city': 'Paris', 'description': 'desc', 'price_unit': 'heure'})
        self.assertRedirects(response, reverse('home'))
        
        # Test provider can create
        self.client.force_login(self.provider)
        response = self.client.post(url, {'title': 'Nouveau Service', 'category': self.category.pk, 'price': 100.0, 'city': 'Paris', 'description': 'desc', 'price_unit': 'heure'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Service.objects.filter(title='Nouveau Service').exists())

    def test_search_filtering(self):
        url = reverse('service_list')
        
        # Filter by city
        response = self.client.get(url, {'city': 'Paris'})
        self.assertContains(response, 'Réparation Fuite')
        self.assertNotContains(response, 'Installation')
        
        # Filter by price up to 100
        response = self.client.get(url, {'max_price': '100'})
        self.assertContains(response, 'Réparation Fuite')
        self.assertNotContains(response, 'Installation')
        
        # Filter by category
        response = self.client.get(url, {'category': self.category.pk})
        self.assertContains(response, 'Réparation Fuite')
        self.assertContains(response, 'Installation')
