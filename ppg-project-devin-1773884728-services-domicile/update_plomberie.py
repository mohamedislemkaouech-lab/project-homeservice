import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category

c = Category.objects.filter(name__icontains='Plomberie').first()
if c:
    desc = """Service de Plomberie Rapide
Installation, réparation et entretien de tuyaux, robinets et systèmes de plomberie pour particuliers et professionnels. Service rapide et efficace.
👉 Vos installations d’eau toujours fonctionnelles."""
    c.description = desc
    
    if os.path.exists('plomberie.jpg'):
        with open('plomberie.jpg', 'rb') as f:
            c.image.save('plomberie.jpg', File(f), save=False)
    
    c.save()
    print('Successfully updated plomberie category.')
else:
    print('Category not found.')
