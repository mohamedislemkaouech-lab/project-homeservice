from django.test import TestCase
from .models import User

class UserRoleTest(TestCase):
    def test_superuser_auto_admin_role(self):
        # Create a superuser via the manager
        user = User.objects.create_superuser(
            username='adminuser',
            password='password123',
            email='admin@example.com'
        )
        # Check if the role was automatically set to 'admin'
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_admin)

    def test_staff_auto_admin_role(self):
        # Create a staff user
        user = User.objects.create_user(
            username='staffuser',
            password='password123',
            is_staff=True
        )
        # Check if the role was automatically set to 'admin'
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_admin)

    def test_regular_user_default_client_role(self):
        # Create a regular user
        user = User.objects.create_user(
            username='clientuser',
            password='password123'
        )
        # Check if the role is 'client' by default
        self.assertEqual(user.role, 'client')
        self.assertTrue(user.is_client)

    def test_manual_role_assignment(self):
        # Manually set a role during creation
        user = User.objects.create_user(
            username='provideruser',
            password='password123',
            role='prestataire'
        )
        self.assertEqual(user.role, 'prestataire')
        self.assertTrue(user.is_prestataire)

from django.urls import reverse
from django.test import Client

class AccountsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create_user(
            username='client1', password='pass_client1', email='cl1@test.com', role='client'
        )
        self.user_prestataire = User.objects.create_user(
            username='prest1', password='pass_prest1', email='pr1@test.com', role='prestataire'
        )

    def test_login_logout(self):
        # Login
        response = self.client.post(reverse('login'), {'username': 'client1', 'password': 'pass_client1'})
        self.assertEqual(response.status_code, 302)
        # Logout
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_registration_client(self):
        url = reverse('register_client')
        data = {
            'username': 'newclient', 'first_name': 'A', 'last_name': 'B',
            'email': 'ncl@test.com', 'phone': '123', 'city': 'Paris',
            'password1': 'testpass123', 'password2': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newclient', role='client').exists())

    def test_registration_prestataire(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = reverse('register_prestataire')
        doc = SimpleUploadedFile("id.pdf", b"file_content", content_type="application/pdf")
        data = {
            'username': 'newprest', 'first_name': 'C', 'last_name': 'D',
            'email': 'npr@test.com', 'phone': '1234', 'city': 'Lyon',
            'address': '123 Rue', 'bio': 'expert', 'identity_document': doc,
            'password1': 'testpass123', 'password2': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newprest', role='prestataire').exists())

    def test_profile_update(self):
        self.client.force_login(self.user_client)
        url = reverse('profile_edit')
        from django.core.files.uploadedfile import SimpleUploadedFile
        doc = SimpleUploadedFile("id2.pdf", b"file_content", content_type="application/pdf")
        data = {
            'first_name': 'Updated', 'last_name': 'Name',
            'email': 'upd@test.com', 'phone': '999',
            'city': 'Marseille', 'address': '44 av', 'bio': '',
            'identity_document': doc
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.user_client.refresh_from_db()
        self.assertEqual(self.user_client.first_name, 'Updated')
