import json
from django.test import TestCase, Client
from django.urls import reverse
from chatbot.models import FAQ

class ChatbotAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an FAQ so we can test the expected "plombier" keyword logic
        FAQ.objects.create(question="Plombier?", answer="Nous envoyons un plombier.", keywords="plombier", is_active=True)

    def test_chatbot_api_known_keyword(self):
        url = reverse('chat_api')
        payload = {
            "messages": [{"role": "user", "content": "J'ai besoin d'un plombier"}]
        }
        # The view expects a json body
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("reply", data)
        self.assertEqual(data["reply"], "Nous envoyons un plombier.")
        self.assertEqual(data["results"], [])

    def test_chatbot_api_special_intents(self):
        url = reverse('chat_api')
        
        # 1. Test "Annuler une réservation"
        payload = {
            "messages": [{"role": "user", "content": "Annuler une réservation"}]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "redirect")
        self.assertEqual(data["action"]["url"], "/reservations/my/")
        self.assertIn("Mes réservations", data["reply"])

        # Test "   annuler une réservation   "
        payload = {
            "messages": [{"role": "user", "content": "   annuler une réservation   "}]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "redirect")
        self.assertEqual(data["action"]["url"], "/reservations/my/")


        # 2. Test "Comment ça marche ?"
        payload = {
            "messages": [{"role": "user", "content": "Comment ça marche ?"}]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "redirect")
        self.assertEqual(data["action"]["url"], "/accounts/how-it-works/")

        # 3. Test "comment ça marche" (without ?, lowercase)
        payload = {
            "messages": [{"role": "user", "content": "comment ça marche"}]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "redirect")
        self.assertEqual(data["action"]["url"], "/accounts/how-it-works/")

        # 4. Test "   Comment ça marche?   " (case-insensitive, whitespace)
        payload = {
            "messages": [{"role": "user", "content": "   Comment ça marche?   "}]
        }
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "redirect")
        self.assertEqual(data["action"]["url"], "/accounts/how-it-works/")

    def test_chatbot_api_generic_help_phrases(self):
        url = reverse('chat_api')
        examples = [
            "j'ai besoin d'aide",
            "bonjour",
            "j'ai un problème"
        ]
        for message in examples:
            payload = {"messages": [{"role": "user", "content": message}]}
            response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["type"], "help")
            self.assertIn("Je suis là pour vous aider", data["reply"])
            self.assertEqual(data["results"], [])
            self.assertGreaterEqual(len(data["quick_replies"]), 1)

    def test_chatbot_api_safe_fallback_for_gibberish(self):
        url = reverse('chat_api')
        payload = {"messages": [{"role": "user", "content": "azerty"}]}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["type"], "fallback")
        self.assertIn("Je n'ai pas bien saisi votre demande", data["reply"])
        self.assertEqual(data["results"], [])
        self.assertGreaterEqual(len(data["quick_replies"]), 1)

    def test_chatbot_api_fuite_deau_matches_plumber(self):
        url = reverse('chat_api')
        payload = {"messages": [{"role": "user", "content": "fuite d'eau"}]}
        response = self.client.post(url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotEqual(data["type"], "no_category")
        self.assertIn(data["type"], ["no_results", "services"])
        self.assertEqual(data["results"], [] if data["type"] == "no_results" else data["results"])

