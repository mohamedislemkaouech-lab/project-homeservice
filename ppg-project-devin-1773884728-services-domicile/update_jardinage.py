import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category

c = Category.objects.filter(name__icontains='Jardinage').first()
if c:
    desc = """Service de Jardinage Professionnel
Entretien complet de votre jardin : tonte, plantation, taille et nettoyage. Nous gardons vos espaces verts propres, sains et esthétiques toute l’année.
👉 Profitez d’un jardin toujours impeccable."""
    c.description = desc
    
    if os.path.exists('jardinage.jpeg'):
        with open('jardinage.jpeg', 'rb') as f:
            c.image.save('jardinage.jpeg', File(f), save=False)
    
    c.save()
    print('Successfully updated jardinage category.')
else:
    print('Category not found.')
