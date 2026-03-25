import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category

c = Category.objects.filter(name__icontains='Baby').first()
if c:
    desc = """Service de Babysitting Fiable
Des baby-sitters sérieux et attentionnés pour garder vos enfants en toute sécurité. Horaires flexibles, activités ludiques, aide aux devoirs et accompagnement personnalisé.
👉 Votre tranquillité d’esprit est notre priorité."""
    c.description = desc
    
    if os.path.exists('baby.jpg'):
        with open('baby.jpg', 'rb') as f:
            c.image.save('baby.jpg', File(f), save=False)
    
    c.save()
    print('Successfully updated baby-sitting category.')
else:
    print('Category not found.')
