import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category

c = Category.objects.filter(name__icontains='Ménage').first()
if c:
    desc = """Service de Ménage Fiable
Nettoyage professionnel pour maisons, bureaux et locaux commerciaux. Résultats impeccables grâce à des méthodes sûres et efficaces.
👉 Un espace propre, l’esprit tranquille."""
    c.description = desc
    
    if os.path.exists('menage.jpg'):
        with open('menage.jpg', 'rb') as f:
            c.image.save('menage.jpg', File(f), save=False)
    
    c.save()
    print('Successfully updated menage category.')
else:
    print('Category not found.')
