import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from services.models import Service
from services.nlp_parser import BookingQueryParser
from chatbot.models import FAQ
from django.urls import reverse

@method_decorator(csrf_exempt, name='dispatch')
class SearchAPIView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parser = BookingQueryParser()

    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
            messages = body.get("messages", [])

            if not messages:
                return JsonResponse({"error": "Aucun message fourni."}, status=400)

            user_message = next(
                (msg['content'] for msg in reversed(messages) if msg['role'] == 'user'),
                None
            )

            if not user_message:
                return JsonResponse({"reply": "Comment puis-je vous aider ?"})

            # ── 1. FAQ check first ─────────────────────────────────────────
            faq_reply = self._check_faq(user_message)
            if faq_reply:
                return JsonResponse({
                    "reply": faq_reply,
                    "type": "faq",
                    "results": [],
                    "quick_replies": self._default_quick_replies()
                })

            # ── 2. Service NLP search ──────────────────────────────────────
            filters = self.parser.parse(user_message)
            services = Service.objects.filter(is_active=True).select_related('provider', 'category')

            if filters.get('service'):
                services = services.filter(category__name__icontains=filters['service'])

            results_count = services.count()
            services = services[:3]

            if not services.exists():
                return JsonResponse({
                    "reply": "Désolé, je n'ai trouvé aucun prestataire disponible pour votre recherche.",
                    "type": "no_results",
                    "filters_applied": filters,
                    "results": [],
                    "quick_replies": self._default_quick_replies()
                })

            results = []
            for s in services:
                results.append({
                    "provider_name": s.provider.get_full_name(),
                    "service_title": s.title,
                    "price": f"{s.price} DT",
                    "url": reverse('service_detail', kwargs={'pk': s.pk}),
                    "book_url": reverse('create_reservation', kwargs={'service_pk': s.pk}),
                })

            service_label = filters.get('service') or 'services'
            reply_text = f"J'ai trouvé {results_count} prestataire(s) pour : {service_label}"

            return JsonResponse({
                "reply": reply_text,
                "type": "services",
                "filters_applied": filters,
                "results": results,
                "quick_replies": [
                    "Voir tous les services",
                    "Annuler une réservation",
                    "Comment ça marche ?",
                ]
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON invalide."}, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": f"Erreur: {str(e)}"}, status=500)

    def _check_faq(self, user_message):
        """Return FAQ answer if any keyword matches the user message."""
        msg_lower = user_message.lower()
        faqs = FAQ.objects.filter(is_active=True).order_by('order')
        for faq in faqs:
            keywords = [k.strip().lower() for k in faq.keywords.split(',') if k.strip()]
            if any(kw in msg_lower for kw in keywords):
                return faq.answer
        return None

    def _default_quick_replies(self):
        return [
            "Plombier",
            "Ménage",
            "Baby-sitting",
            "Comment ça marche ?",
        ]