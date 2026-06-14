from decimal import Decimal
from django.db import migrations


def seed_electricite_service(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Category = apps.get_model('services', 'Category')
    Service = apps.get_model('services', 'Service')

    provider, created = User.objects.get_or_create(
        username='electricien_prestataire',
        defaults={
            'email': 'electricien@example.com',
            'first_name': 'Électricien',
            'last_name': 'Prestataire',
            'role': 'prestataire',
            'is_active': True,
        }
    )
    if provider.role != 'prestataire':
        provider.role = 'prestataire'
        provider.save()

    category = Category.objects.filter(name__icontains='lectric').first()
    if not category:
        category = Category.objects.filter(name__icontains='electric').first()

    if category:
        Service.objects.get_or_create(
            title='Électricien à domicile',
            provider=provider,
            category=category,
            defaults={
                'description': 'Service d\'électricité à domicile : dépannage et installation rapide.',
                'price': Decimal('120.00'),
                'price_unit': 'heure',
                'city': 'Tunis',
                'address': 'Rue de l\'Électricité 1',
                'is_active': True,
            }
        )


def unseed_electricite_service(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Service = apps.get_model('services', 'Service')

    services = Service.objects.filter(title='Électricien à domicile')
    services.delete()
    User.objects.filter(username='electricien_prestataire').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_identity_document_user_verification_status'),
        ('services', '0003_seed_categories'),
    ]

    operations = [
        migrations.RunPython(seed_electricite_service, unseed_electricite_service),
    ]
