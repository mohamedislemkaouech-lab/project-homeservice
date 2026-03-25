import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category

c = Category.objects.filter(name__icontains='ménagement').first()
if c:
    desc = """Service de Déménagement Fiable
Des solutions rapides et sécurisées pour vos déménagements résidentiels et professionnels. Emballage, transport et livraison en toute sécurité.
👉 Déménagez en toute sérénité avec notre équipe."""
    c.description = desc
    
    if os.path.exists('demenagement.webp'):
        with open('demenagement.webp', 'rb') as f:
            c.image.save('demenagement.webp', File(f), save=False)
    
    c.save()
    print('Successfully updated demenagement category.')
else:
    print('Category not found.')
