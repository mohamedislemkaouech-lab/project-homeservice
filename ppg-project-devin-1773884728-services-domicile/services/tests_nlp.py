from django.test import TestCase
from django.utils import timezone
from services.nlp_parser import BookingQueryParser
from datetime import timedelta

class NLPBookingQueryParserTests(TestCase):
    def setUp(self):
        self.parser = BookingQueryParser()
        self.today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    def test_plumber_urgent_tomorrow(self):
        query = "Je cherche un plombier pour demain urgent"
        result = self.parser.parse(query)
        
        self.assertEqual(result['service'], 'Plomberie')
        self.assertEqual(result['urgency'], 'urgent')
        self.assertIsNotNone(result['date_min'])
        
        expected_date = self.today + timedelta(days=1)
        self.assertEqual(result['date_min'], expected_date)

    def test_electrician_this_week_evening(self):
        query = "Besoin électricien cette semaine après 18h"
        result = self.parser.parse(query)
        
        self.assertEqual(result['service'], 'Électricité')
        self.assertEqual(result['time_preference'], 'evening')
        self.assertEqual(result['date_min'], self.today)
        self.assertEqual(result['date_max'], self.today + timedelta(days=7))

    def test_nanny_monday_morning(self):
        query = "Nounou disponible lundi et mercredi matin"
        result = self.parser.parse(query)
        
        self.assertEqual(result['service'], 'Baby-sitting')
        self.assertEqual(result['time_preference'], 'morning')
        
        # Will pick up the first day it encounters, likely lundi
        self.assertIsNotNone(result['date_min'])
        self.assertEqual(result['date_min'].weekday(), 0) # 0 is Monday

    def test_gardener_weekend(self):
        query = "Je veux un jardinier ce week-end"
        result = self.parser.parse(query)
        
        self.assertEqual(result['service'], 'Jardinage')
        self.assertIsNotNone(result['date_min'])
        self.assertEqual(result['date_min'].weekday(), 5) # 5 is Saturday
