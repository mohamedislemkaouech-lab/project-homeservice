import re
import json
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

class BookingQueryParser:
    def __init__(self):
        # Category mappings
        self.service_keywords = {
            'Plomberie': ['plombier', 'fuite', 'robinet', 'tuyau', 'évier', 'déboucher', 'chasse', 'eau'],
            'Électricité': ['électricien', 'courant', 'prise', 'ampoule', 'disjoncteur', 'lumière', 'panne électrique'],
            'Jardinage': ['jardinier', 'tonte', 'gazon', 'plante', 'arbre', 'taille', 'arrosage'],
            'Ménage': ['femme de ménage', 'nettoyage', 'propre', 'vitres', 'poussière', 'sol', 'ménage'],
            'Baby-sitting': ['nounou', 'baby sitter', 'baby-sitter', 'enfant', 'garde', 'bébé'],
            'Déménagement': ['déménageur', 'carton', 'camion', 'transporter', 'meuble'],
            'Climatisation': ['clim', 'climatiseur', 'gaz', 'fuite clim', 'froid', 'chaud', 'chauffage'],
            'Peinture': ['peintre', 'peinture', 'mur', 'plafond', 'couleur', 'pinceau']
        }
        
        # Urgency markers
        self.urgence_keywords = ['urgent', 'immédiat', 'cassé', 'panne', 'vite', 'urgence', 'au plus vite', 'rapidement']
        
        # Time preference markers
        self.time_preferences = {
            'morning': ['matin', 'matinée', 'avant midi', 'aube'],
            'afternoon': ['après-midi', 'apres midi', 'apres-midi'],
            'evening': ['soir', 'soirée', 'nuit']
        }
    
    def parse(self, user_input: str) -> dict:
        user_input_lower = user_input.lower()
        
        result = {
            'service': None,
            'date_min': None,
            'date_max': None,
            'urgency': 'normal',
            'time_preference': None,
            'keywords': [],
            'confidence': 0.0
        }
        
        confidence_score = 0.0
        
        # 1. Detect service
        for category, keywords in self.service_keywords.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', user_input_lower):
                    result['service'] = category
                    result['keywords'].append(kw)
                    confidence_score += 0.4
                    break
                    
        # 2. Detect urgency
        for kw in self.urgence_keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', user_input_lower):
                result['urgency'] = 'urgent'
                result['keywords'].append(kw)
                confidence_score += 0.2
                break
                
        # 3. Detect time preference
        for pref, keywords in self.time_preferences.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', user_input_lower):
                    result['time_preference'] = pref
                    result['keywords'].append(kw)
                    confidence_score += 0.2
                    break
                    
        # 4. Temporal parsing
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if re.search(r'\baujourd\'?hui\b', user_input_lower):
            result['date_min'] = today
            result['date_max'] = today + timedelta(days=1)
            confidence_score += 0.3
        elif re.search(r'\bdemain\b', user_input_lower):
            result['date_min'] = today + timedelta(days=1)
            result['date_max'] = today + timedelta(days=2)
            confidence_score += 0.3
        elif re.search(r'\baprès[- ]demain\b', user_input_lower):
            result['date_min'] = today + timedelta(days=2)
            result['date_max'] = today + timedelta(days=3)
            confidence_score += 0.3
        elif re.search(r'\bcette semaine\b', user_input_lower):
            result['date_min'] = today
            result['date_max'] = today + timedelta(days=7)
            confidence_score += 0.3
        elif re.search(r'\bweek-?end\b', user_input_lower):
            days_ahead_sat = 5 - today.weekday()
            if days_ahead_sat <= 0:
                days_ahead_sat += 7
            next_sat = today + timedelta(days=days_ahead_sat)
            result['date_min'] = next_sat
            result['date_max'] = next_sat + timedelta(days=2)
            confidence_score += 0.3
            
        # Specific days
        days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        for i, day in enumerate(days):
            if re.search(r'\b' + day + r'\b', user_input_lower):
                days_ahead = i - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                target_day = today + timedelta(days=days_ahead)
                result['date_min'] = target_day
                result['date_max'] = target_day + timedelta(days=1)
                confidence_score += 0.3
                break
                
        # Time parsing e.g. "entre 9h et 12h"
        time_match = re.search(r'entre (\d{1,2})h et (\d{1,2})h', user_input_lower)
        if time_match:
            start_h = int(time_match.group(1))
            if start_h < 12:
                result['time_preference'] = 'morning'
            elif start_h < 18:
                result['time_preference'] = 'afternoon'
            else:
                result['time_preference'] = 'evening'
            confidence_score += 0.2
        elif re.search(r'après (\d{1,2})h', user_input_lower):
            start_h = int(re.search(r'après (\d{1,2})h', user_input_lower).group(1))
            if start_h >= 18:
                result['time_preference'] = 'evening'
            elif start_h >= 12:
                result['time_preference'] = 'afternoon'
            confidence_score += 0.2

        result['confidence'] = min(confidence_score, 1.0)
        
        # VERSION 2: LLM Fallback
        if result['confidence'] < 0.7 or not result['service']:
            llm_result = self._fallback_llm_parse(user_input)
            if llm_result and llm_result.get('service'):
                # Valid LLM Extraction
                result['service'] = llm_result.get('service')
                result['urgency'] = llm_result.get('urgency', 'normal')
                result['time_preference'] = llm_result.get('time_preference')
                result['confidence'] = 0.9
                
        return result

    def _fallback_llm_parse(self, text: str) -> dict:
        API_URL = "https://openrouter.ai/api/v1/chat/completions"
        api_key = getattr(settings, 'OPENROUTER_API_KEY', 'sk-or-v1-3c3f7c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c')
        
        prompt = (
            "Extrais le service, la date et l'urgence du texte suivant. "
            "Réponds UNIQUEMENT avec un objet JSON strict au format exact: "
            "{\"service\": \"Plomberie|Électricité|Jardinage|Ménage|Baby-sitting|Déménagement|Climatisation|Peinture|null\", "
            "\"urgency\": \"urgent|normal\", "
            "\"time_preference\": \"morning|afternoon|evening|null\"}. "
            f"Texte: '{text}'"
        )
        
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "google/gemini-2.5-flash",
                "messages": [{"role": "user", "content": prompt}]
            }
            
            resp = requests.post(API_URL, headers=headers, json=data, timeout=5)
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                content = content.replace('```json', '').replace('```', '').strip()
                return json.loads(content)
        except Exception:
            pass
            
        return None
