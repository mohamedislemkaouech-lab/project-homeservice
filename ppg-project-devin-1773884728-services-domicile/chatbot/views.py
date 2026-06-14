import json
import logging
import unicodedata
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from services.models import Service
from services.nlp_parser import BookingQueryParser
from chatbot.models import FAQ
from django.urls import reverse

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    normalized = text.lower().replace("'", " ").replace("’", " ").strip()
    normalized = unicodedata.normalize('NFD', normalized)
    normalized = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
    return ' '.join(normalized.split())

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

            normalized_message = normalize_text(user_message)

            # ── 0. Special intent shortcuts ───────────────────────
            SPECIAL_INTENTS = {
                'voir tous les services': {
                    "reply": "Voici tous nos services disponibles sur la plateforme.",
                    "type": "redirect",
                    "results": [],
                    "action": {"type": "link", 
                               "label": "Voir tous les services",
                               "url": "/services/"},
                    "quick_replies": self._default_quick_replies()
                },
                'tous les services': {
                    "reply": "Voici tous nos services disponibles sur la plateforme.",
                    "type": "redirect", 
                    "results": [],
                    "action": {"type": "link",
                               "label": "Voir tous les services", 
                               "url": "/services/"},
                    "quick_replies": self._default_quick_replies()
                },
                'annuler une réservation': {
                    "reply": "Vous pouvez annuler une réservation en attente depuis votre tableau de bord. Allez dans \"Mes réservations\" et cliquez sur \"Annuler\".",
                    "type": "redirect",
                    "results": [],
                    "action": {"type": "link",
                               "label": "Mes réservations",
                               "url": "/reservations/my/"},
                    "quick_replies": self._default_quick_replies()
                },
                'comment ça marche ?': {
                    "reply": "Notre plateforme permet de mettre en relation des particuliers avec des prestataires de services à domicile. Recherchez un service, consultez les profils et réservez en ligne !",
                    "type": "redirect",
                    "results": [],
                    "action": {"type": "link",
                               "label": "Comment ça marche",
                               "url": "/accounts/how-it-works/"},
                    "quick_replies": self._default_quick_replies()
                },
                'comment ça marche?': {
                    "reply": "Notre plateforme permet de mettre en relation des particuliers avec des prestataires de services à domicile. Recherchez un service, consultez les profils et réservez en ligne !",
                    "type": "redirect",
                    "results": [],
                    "action": {"type": "link",
                               "label": "Comment ça marche",
                               "url": "/accounts/how-it-works/"},
                    "quick_replies": self._default_quick_replies()
                },
                'comment ça marche': {
                    "reply": "Notre plateforme permet de mettre en relation des particuliers avec des prestataires de services à domicile. Recherchez un service, consultez les profils et réservez en ligne !",
                    "type": "redirect",
                    "results": [],
                    "action": {"type": "link",
                               "label": "Comment ça marche",
                               "url": "/accounts/how-it-works/"},
                    "quick_replies": self._default_quick_replies()
                },
            }
            
            normalized_special_intents = {
                normalize_text(k): v for k, v in SPECIAL_INTENTS.items()
            }
            if normalized_message in normalized_special_intents:
                return JsonResponse(normalized_special_intents[normalized_message])

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
            service_query = filters.get('service')
            
            # If no service category detected at all, try generic help or fallback
            if not service_query:
                GENERIC_HELP_KEYWORDS = [
                    'aide', 'besoin', 'probleme', 'help', 'bonjour', 'salut',
                    'quelquun', 'cherche'
                ]
                if any(keyword in normalized_message for keyword in GENERIC_HELP_KEYWORDS):
                    return JsonResponse({
                        "reply": (
                            "Je suis là pour vous aider ! Quel type de service recherchez-vous ? "
                            "Par exemple : plombier, ménage, baby-sitting, électricien..."
                        ),
                        "type": "help",
                        "results": [],
                        "quick_replies": self._default_quick_replies()
                    })

                return JsonResponse({
                    "reply": "Je n'ai pas bien saisi votre demande. Voici ce que je peux faire pour vous :",
                    "type": "fallback",
                    "results": [],
                    "quick_replies": self._default_quick_replies()
                })
            
            # Only search if we have a category
            services = Service.objects.filter(is_active=True).select_related(
                'provider', 'category'
            )
            services = services.filter(
                category__name__icontains=service_query
            )
            
            results_count = services.count()

            # --- Location prioritization / user awareness ---
            user_city = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_city = getattr(request.user, 'city', None)
                if user_city:
                    user_city_norm = user_city.strip().lower()
                    # sort so providers in same city come first
                    services = sorted(list(services), key=lambda s: 0 if (
                        (s.city and s.city.strip().lower() == user_city_norm) or
                        (getattr(s.provider, 'city', None) and getattr(s.provider, 'city').strip().lower() == user_city_norm)
                    ) else 1)
                else:
                    services = list(services)
            else:
                services = list(services)

            # limit to top 3
            services = services[:3]

            # If no services at all
            if not services:
                return JsonResponse({
                    "reply": f"Désolé, je n'ai trouvé aucun prestataire "
                             f"disponible pour \"{service_query}\" "
                             f"pour le moment.",
                    "type": "no_results",
                    "results": [],
                    "quick_replies": self._default_quick_replies()
                })
            
            # Determine if we should display a region note
            location_note = None
            if hasattr(request, 'user') and request.user.is_authenticated and user_city:
                matched = any(((s.city and s.city.strip().lower() == user_city_norm) or
                               (getattr(s.provider, 'city', None) and getattr(s.provider, 'city').strip().lower() == user_city_norm)) for s in services)
                if not matched:
                    location_note = "(Prestataires disponibles dans votre région)"
            else:
                # user not logged in or no city information
                location_note = "(Prestataires disponibles dans votre région)"

            results = []
            for s in services:
                # display rating next to price
                try:
                    rating = float(s.average_rating) if s.average_rating else None
                except Exception:
                    rating = None
                if rating:
                    price_display = f"⭐ {rating} · {s.price} DT"
                else:
                    price_display = f"{s.price} DT"

                # booking / login handling
                if hasattr(request, 'user') and request.user.is_authenticated:
                    book_info = {"book_url": reverse('create_reservation', kwargs={'service_pk': s.pk})}
                else:
                    book_info = {"login_required": True, "login_url": "/accounts/login/", "login_message": "Connectez-vous pour réserver"}

                provider_city = s.city or getattr(s.provider, 'city', None) or ''

                entry = {
                    "provider_name": s.provider.get_full_name(),
                    "service_title": s.title,
                    "price_display": price_display,
                    "url": reverse('service_detail', kwargs={'pk': s.pk}),
                    "provider_city": provider_city,
                }
                entry.update(book_info)
                results.append(entry)
            
            service_label = service_query
            reply_text = (f"J'ai trouvé {results_count} prestataire(s) "
                          f"pour : {service_label} {location_note or ''}")
            
            return JsonResponse({
                "reply": reply_text,
                "type": "services",
                "filters_applied": filters,
                "results": results,
                "note": location_note,
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