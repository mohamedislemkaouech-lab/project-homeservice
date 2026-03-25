import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category

cs = Category.objects.filter(name__exact='Déménagement')
desc_demenagement = """Service de Déménagement Fiable
Des solutions rapides et sécurisées pour vos déménagements résidentiels et professionnels. Emballage, transport et livraison en toute sécurité.
👉 Déménagez en toute sérénité avec notre équipe."""

for c in cs:
    c.description = desc_demenagement
    if os.path.exists('demenagement.webp'):
        with open('demenagement.webp', 'rb') as f:
            c.image.save('demenagement.webp', File(f), save=False)
    c.save()
    print(f'Fixed category: {c.id} - {c.name}')
