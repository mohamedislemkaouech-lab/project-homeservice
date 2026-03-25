from django.core.management.base import BaseCommand
from accounts.models import User
from services.models import Category, Service, Availability
from chatbot.models import FAQ


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding categories...')
        categories_data = [
            {'name': 'Plomberie', 'description': 'Réparation et installation de plomberie', 'icon': 'fa-faucet'},
            {'name': 'Électricité', 'description': 'Travaux et dépannage électrique', 'icon': 'fa-bolt'},
            {'name': 'Ménage', 'description': 'Nettoyage et entretien de maison', 'icon': 'fa-broom'},
            {'name': 'Baby-sitting', 'description': 'Garde d\'enfants à domicile', 'icon': 'fa-baby'},
            {'name': 'Jardinage', 'description': 'Entretien de jardin et espaces verts', 'icon': 'fa-leaf'},
            {'name': 'Peinture', 'description': 'Peinture intérieure et extérieure', 'icon': 'fa-paint-roller'},
            {'name': 'Déménagement', 'description': 'Aide au déménagement et transport', 'icon': 'fa-truck'},
            {'name': 'Climatisation', 'description': 'Installation et maintenance de climatisation', 'icon': 'fa-snowflake'},
        ]
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f'  Created category: {cat.name}')

        self.stdout.write('Seeding FAQ...')
        faqs_data = [
            {
                'question': 'Comment fonctionne la plateforme ?',
                'answer': 'Notre plateforme permet de mettre en relation des particuliers avec des prestataires de services à domicile. Recherchez un service, consultez les profils et réservez en ligne !',
                'keywords': 'fonctionnement, plateforme, comment ça marche, marche',
                'order': 1,
            },
            {
                'question': 'Comment annuler une réservation ?',
                'answer': 'Vous pouvez annuler une réservation en attente depuis votre tableau de bord. Allez dans "Mes réservations" et cliquez sur "Annuler".',
                'keywords': 'annuler, annulation, supprimer réservation',
                'order': 2,
            },
            {
                'question': 'Comment devenir prestataire ?',
                'answer': 'Inscrivez-vous en tant que prestataire, complétez votre profil, ajoutez vos services et définissez vos disponibilités. Les clients pourront alors vous contacter et réserver vos services.',
                'keywords': 'devenir prestataire, proposer service, offrir service',
                'order': 3,
            },
            {
                'question': 'Les paiements sont-ils sécurisés ?',
                'answer': 'Le paiement se fait directement entre le client et le prestataire après la réalisation du service. Nous ne gérons pas les transactions financières pour le moment.',
                'keywords': 'paiement, payer, argent, sécurisé, transaction',
                'order': 4,
            },
        ]
        for faq_data in faqs_data:
            faq, created = FAQ.objects.get_or_create(question=faq_data['question'], defaults=faq_data)
            if created:
                self.stdout.write(f'  Created FAQ: {faq.question[:50]}')

        self.stdout.write(self.style.SUCCESS('Seed data created successfully!'))
