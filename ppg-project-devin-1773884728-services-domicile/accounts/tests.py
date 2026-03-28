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
