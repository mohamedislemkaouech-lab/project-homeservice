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
