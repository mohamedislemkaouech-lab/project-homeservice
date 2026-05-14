from django.db import migrations


CATEGORIES = [
    {
        'name': 'Baby-sitting',
        'icon': 'fa-baby',
        'description': 'Service de garde d\'enfants à domicile par des professionnels qualifiés et de confiance.',
    },
    {
        'name': 'Climatisation',
        'icon': 'fa-snowflake',
        'description': 'Service de Climatisation Professionnel Installation, entretien et réparation de systèmes de climatisation pour particuliers et professionnels. Nous garantissons performance, efficacité énergétique et confort toute l\'année. 👉 Restez au frais avec un service fiable.',
    },
    {
        'name': 'Déménagement',
        'icon': 'fa-truck',
        'description': 'Service de déménagement professionnel pour particuliers et entreprises. Transport sécurisé de vos biens avec soin et efficacité.',
    },
    {
        'name': 'Jardinage',
        'icon': 'fa-leaf',
        'description': 'Entretien de jardins, taille de haies, tonte de pelouse et aménagement paysager par des jardiniers expérimentés.',
    },
    {
        'name': 'Ménage',
        'icon': 'fa-broom',
        'description': 'Service de nettoyage et ménage à domicile. Des professionnels pour garder votre intérieur impeccable.',
    },
    {
        'name': 'Peinture',
        'icon': 'fa-paint-roller',
        'description': 'Travaux de peinture intérieure et extérieure par des peintres qualifiés. Finitions soignées et matériaux de qualité.',
    },
    {
        'name': 'Plomberie',
        'icon': 'fa-faucet',
        'description': 'Réparation et installation de plomberie à domicile. Intervention rapide pour fuites, canalisations et sanitaires.',
    },
    {
        'name': 'Electricité',
        'icon': 'fa-bolt',
        'description': 'Services électriques professionnels : installation, dépannage et mise aux normes par des électriciens certifiés.',
    },
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('services', 'Category')
    for cat in CATEGORIES:
        Category.objects.get_or_create(
            name=cat['name'],
            defaults={
                'icon': cat['icon'],
                'description': cat['description'],
            }
        )


def unseed_categories(apps, schema_editor):
    Category = apps.get_model('services', 'Category')
    names = [c['name'] for c in CATEGORIES]
    Category.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_category_image'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
