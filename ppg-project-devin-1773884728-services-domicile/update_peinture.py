import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category

c = Category.objects.filter(name__icontains='Peinture').first()
if c:
    desc = """Service de Peinture Professionnel
Peinture intérieure et extérieure de qualité pour maisons, bureaux et locaux commerciaux. Finitions parfaites et durables garanties.
👉 Sublimez vos espaces avec notre expertise."""
    c.description = desc
    
    if os.path.exists('peinture.jpg'):
        with open('peinture.jpg', 'rb') as f:
            c.image.save('peinture.jpg', File(f), save=False)
    
    c.save()
    print('Successfully updated peinture category.')
else:
    print('Category not found.')
