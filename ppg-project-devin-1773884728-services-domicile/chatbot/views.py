# chatbot/views.py
# Django view that proxies chat requests from the frontend to Ollama (tinyllama model) running locally.
# Accepts POST /chatbot/api/chat/ with a full 'messages' conversation history,
# forwards to Ollama, and returns {"reply": "..."}.

import json
import requests as http_requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import ChatMessage, FAQ
from services.models import Service, Category

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "tinyllama"

SYSTEM_PROMPT = """Tu es un assistant virtuel pour ServicesDOM, une plateforme tunisienne de services à domicile.
Tu aides les utilisateurs à trouver des prestataires, comprendre comment réserver, et répondre à leurs questions.
Réponds toujours en français. Sois concis, amical et professionnel.
Si tu ne sais pas quelque chose, dis-le honnêtement plutôt que d'inventer."""


@csrf_exempt
@require_POST
def chat_api(request):
    """Original keyword-based chat endpoint at /chatbot/api/."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')

        if not user_message:
            return JsonResponse({'error': 'Message vide'}, status=400)

        response = get_chatbot_response(user_message)

        ChatMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key or '',
            message=user_message,
            response=response
        )

        return JsonResponse({'response': response})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Format invalide'}, status=400)
    except Exception:
        return JsonResponse({'error': 'Erreur serveur'}, status=500)


@csrf_exempt
@require_POST
def ollama_chat_api(request):
    """Ollama-powered chat endpoint at /chatbot/api/chat/.
    Accepts: {"messages": [{"role": "user"|"assistant", "content": "..."}]}
    Returns:  {"reply": "..."}
    """
    try:
        data = json.loads(request.body)
        messages = data.get('messages', [])

        if not messages:
            return JsonResponse({'error': 'Aucun message fourni'}, status=400)

        # Prepend system prompt
        ollama_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

        try:
            resp = http_requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "messages": ollama_messages,
                    "stream": False,
                },
                timeout=60,
            )
            resp.raise_for_status()
            reply = resp.json()["message"]["content"]
        except http_requests.exceptions.ConnectionError:
            return JsonResponse(
                {'error': 'Ollama est hors ligne. Vérifiez que le service local tourne sur le port 11434.'},
                status=503
            )
        except Exception as exc:
            return JsonResponse({'error': f'Erreur Ollama : {str(exc)}'}, status=500)

        return JsonResponse({'reply': reply})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Format invalide'}, status=400)
    except Exception:
        return JsonResponse({'error': 'Erreur serveur interne'}, status=500)


# ── Original keyword-based fallback (kept for /chatbot/api/) ──────────────────

def get_chatbot_response(user_message):
    message_lower = user_message.lower().strip()

    faqs = FAQ.objects.filter(is_active=True)
    for faq in faqs:
        keywords = [kw.strip().lower() for kw in faq.keywords.split(',')]
        if any(keyword in message_lower for keyword in keywords):
            return faq.answer

    greetings = ['bonjour', 'salut', 'hello', 'hi', 'hey', 'bonsoir', 'coucou']
    if any(g in message_lower for g in greetings):
        return ("Bonjour ! Bienvenue sur notre plateforme de services à domicile. "
                "Je peux vous aider à :\n"
                "- Trouver un prestataire\n"
                "- Comprendre comment réserver\n"
                "- Répondre à vos questions\n\n"
                "Que souhaitez-vous faire ?")

    search_keywords = ['cherche', 'recherche', 'besoin', 'trouver', 'trouve']
    if any(kw in message_lower for kw in search_keywords):
        categories = Category.objects.all()
        category_names = [cat.name for cat in categories]
        for cat in categories:
            if cat.name.lower() in message_lower:
                services = Service.objects.filter(category=cat, is_active=True)[:5]
                if services:
                    result = f"Voici les services disponibles en {cat.name} :\n\n"
                    for s in services:
                        result += f"- {s.title} par {s.provider.get_full_name()} ({s.city}) - {s.price} DT/{s.get_price_unit_display()}\n"
                    result += "\nCliquez sur un service pour voir les détails et réserver."
                    return result
                else:
                    return f"Désolé, aucun service de {cat.name} n'est disponible pour le moment."
        return ("Je peux vous aider à trouver un prestataire ! "
                f"Voici les catégories disponibles :\n\n"
                + "\n".join([f"- {name}" for name in category_names]) +
                "\n\nQuel type de service recherchez-vous ?")

    booking_keywords = ['réserver', 'reservation', 'réservation', 'comment', 'commander']
    if any(kw in message_lower for kw in booking_keywords):
        return ("Pour réserver un service :\n\n"
                "1. Recherchez le service souhaité\n"
                "2. Consultez le profil du prestataire\n"
                "3. Choisissez une date et un créneau horaire\n"
                "4. Confirmez votre réservation\n\n"
                "Le prestataire recevra votre demande et pourra l'accepter ou la refuser.")

    price_keywords = ['prix', 'tarif', 'coût', 'combien', 'cout']
    if any(kw in message_lower for kw in price_keywords):
        return ("Les tarifs varient selon le prestataire et le type de service. "
                "Chaque prestataire fixe ses propres prix. "
                "Vous pouvez comparer les tarifs en consultant la page des services.")

    thanks_keywords = ['merci', 'remercie', 'thanks']
    if any(kw in message_lower for kw in thanks_keywords):
        return "De rien ! N'hésitez pas si vous avez d'autres questions. Bonne journée !"

    return ("Je n'ai pas bien compris votre demande. Voici ce que je peux faire :\n\n"
            "- Rechercher un service (tapez : 'je cherche un plombier')\n"
            "- Comment réserver (tapez : 'comment réserver')\n"
            "- Infos sur les prix (tapez : 'quels sont les tarifs')\n\n"
            "N'hésitez pas à reformuler votre question !")