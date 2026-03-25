import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.models import Category

c = Category.objects.filter(name__icontains='lectricit').first()
if c:
    desc = """Service d’Électricité Professionnel
Installation, entretien et réparation des systèmes électriques pour particuliers et professionnels. Solutions sûres, fiables et efficaces.
👉 Votre électricité entre de bonnes mains."""
    c.description = desc
    
    if os.path.exists('electricite.jpg'):
        with open('electricite.jpg', 'rb') as f:
            c.image.save('electricite.jpg', File(f), save=False)
    
    c.save()
    print('Successfully updated electricite category.')
else:
    print('Category not found.')
