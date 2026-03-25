import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category

c = Category.objects.filter(name__icontains='Climatisation').first()
if c:
    desc = """Service de Climatisation Professionnel
Installation, entretien et réparation de systèmes de climatisation pour particuliers et professionnels. Nous garantissons performance, efficacité énergétique et confort toute l’année.
👉 Restez au frais avec un service fiable."""
    c.description = desc
    
    if os.path.exists('clima.jpg'):
        with open('clima.jpg', 'rb') as f:
            c.image.save('clima.jpg', File(f), save=False)
    
    c.save()
    print('Successfully updated climatisation category.')
else:
    print('Category not found.')
