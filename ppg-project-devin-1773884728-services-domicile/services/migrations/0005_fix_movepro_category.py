from django.db import migrations


def fix_movepro_categories(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Service = apps.get_model('services', 'Service')
    Category = apps.get_model('services', 'Category')

    dem_cat = Category.objects.filter(name__icontains='déménagement').first() or Category.objects.filter(name__icontains='demenagement').first()
    menage_cat = Category.objects.filter(name__icontains='ménage').first() or Category.objects.filter(name__icontains='menage').first()

    if not dem_cat:
        return

    # Look for providers or services mentioning MovePro (case-insensitive)
    services = Service.objects.filter(title__icontains='movepro') | Service.objects.filter(provider__username__icontains='movepro') | Service.objects.filter(provider__first_name__icontains='movepro') | Service.objects.filter(provider__last_name__icontains='movepro')

    for s in services.distinct():
        # set category to Déménagement
        s.category = dem_cat
        s.save()

    # Additionally, remove any duplicate services for same provider that are in ménage category
    if menage_cat:
        dup_services = Service.objects.filter(category=menage_cat, provider__in=[svc.provider for svc in services.distinct()])
        dup_services.delete()


def reverse_fix(apps, schema_editor):
    # No reversible action
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_seed_electricite_service'),
        ('accounts', '0002_user_identity_document_user_verification_status'),
    ]

    operations = [
        migrations.RunPython(fix_movepro_categories, reverse_fix),
    ]
