import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from services.models import Service
from services.nlp_parser import BookingQueryParser
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
            
            # Retrieve the latest textual query from the user
            user_message = next((msg['content'] for msg in reversed(messages) if msg['role'] == 'user'), None)
            
            if not user_message:
                return JsonResponse({"reply": "Comment puis-je vous aider ?"})

            # Parse query using regex + LLM fallback
            filters = self.parser.parse(user_message)
            
            # Dynamic ORM Request Builders
            services = Service.objects.filter(is_active=True).select_related('provider', 'category')
            
            if filters.get('service'):
                # Handle exact category matching or icontains mapping
                services = services.filter(category__name__icontains=filters['service'])
                
            # (Date filtering and urgency filtering could be expanded further here)

            results_count = services.count()
            services = services[:3] # Cap to 3 for UI purposes
            
            if not services.exists():
                reply_text = f"Désolé, je n'ai trouvé aucun prestataire disponible pour votre recherche."
                return JsonResponse({
                    "reply": reply_text,
                    "filters_applied": filters,
                    "results": []
                })
            
            # Prepare rich JSON array payload
            results = []
            for s in services:
                results.append({
                    "provider_name": s.provider.get_full_name(),
                    "service_title": s.title,
                    "price": f"{s.price} DT",
                    "url": reverse('service_detail', kwargs={'pk': s.pk})
                })

            reply_text = f"🚨 J'ai trouvé {results_count} prestataire(s) correspondant à votre besoin en matière de {filters['service'] or 'services'} :"
            
            return JsonResponse({
                "reply": reply_text,
                "filters_applied": filters,
                "results": results
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON invalide."}, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": f"Erreur du moteur NLP: {str(e)}"}, status=500)