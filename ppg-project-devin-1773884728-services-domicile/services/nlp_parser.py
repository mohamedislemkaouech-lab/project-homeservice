import re
import json
import requests
import logging
import unicodedata
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

class BookingQueryParser:
    def __init__(self):
        # Category mappings
        self.service_keywords = {
            'Plomberie': ['plombier', 'fuite', 'robinet', 'tuyau', 'évier', 'déboucher', 'chasse', 'eau', 'problème eau', 'probleme eau'],
            'Électricité': ['électricien', 'courant', 'prise', 'ampoule', 'disjoncteur', 'lumière', 'panne électrique', 'lumiere', 'prise', 'courant'],
            'Jardinage': ['jardinier', 'tonte', 'gazon', 'plante', 'arbre', 'taille', 'arrosage'],
            'Ménage': ['femme de ménage', 'nettoyage', 'nettoyer', 'propre', 'sale', 'maison sale', 'appartement sale', 'faire le ménage', 'poussière', 'aspirer', 'laver', 'vitres', 'sol', 'ménage'],
            'Baby-sitting': ['nounou', 'baby sitter', 'baby-sitter', 'babysitter', 'enfant', 'garde', 'bébé', 'baby-sitting', 'babysitting', 'baby sitting'],
            'Déménagement': ['déménageur', 'carton', 'camion', 'transporter', 'meuble'],
            'Climatisation': ['clim', 'climatiseur', 'gaz', 'fuite clim', 'froid', 'chaud', 'chauffage'],
            'Peinture': ['peintre', 'peinture', 'mur', 'plafond', 'couleur', 'pinceau']
        }
        
        # Urgency markers
        self.urgence_keywords = ['urgent', 'immédiat', 'cassé', 'panne', 'vite', 'urgence', 'au plus vite', 'rapidement']
        
        # Time preference markers
        self.time_preferences = {
            'morning': ['matin', 'matinee', 'avant midi', 'aube'],
            'afternoon': ['apres-midi', 'apres midi', 'apres-midi'],
            'evening': ['soir', 'soiree', 'nuit']
        }
    
    def _normalize_text(self, text: str) -> str:
        normalized = text.lower().replace("'", " ").replace("’", " ").strip()
        normalized = unicodedata.normalize('NFD', normalized)
        normalized = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
        return ' '.join(normalized.split())

    def parse(self, user_input: str) -> dict:
        normalized_input = self._normalize_text(user_input)
        
        # Direct category name match — highest priority
        DIRECT_TRIGGERS = {
            'baby-sitting':  'Baby-sitting',
            'babysitting':   'Baby-sitting',
            'baby sitting':  'Baby-sitting',
            'plomberie':     'Plomberie',
            'plombier':      'Plomberie',
            'électricité':   'Électricité',
            'electricite':   'Électricité',
            'électricien':   'Électricité',
            'electricien':   'Électricité',
            'ménage':        'Ménage',
            'menage':        'Ménage',
            'nettoyage':     'Ménage',
            'jardinage':     'Jardinage',
            'jardinier':     'Jardinage',
            'peinture':      'Peinture',
            'peintre':       'Peinture',
            'déménagement':  'Déménagement',
            'demenagement':  'Déménagement',
            'climatisation': 'Climatisation',
            'clim':          'Climatisation',
        }
        msg_stripped = normalized_input.strip()
        normalized_direct_triggers = {
            self._normalize_text(k): v for k, v in DIRECT_TRIGGERS.items()
        }
        if msg_stripped in normalized_direct_triggers:
            result = {
                'service': normalized_direct_triggers[msg_stripped],
                'date_min': None,
                'date_max': None,
                'urgency': 'normal',
                'time_preference': None,
                'keywords': [msg_stripped],
                'confidence': 1.0
            }
            return result
        
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
                kw_search = self._normalize_text(kw)
                if re.search(r'\b' + re.escape(kw_search) + r'\b', normalized_input):
                    result['service'] = category
                    result['keywords'].append(kw)
                    confidence_score += 0.4
                    break
                    
        # 2. Detect urgency
        for kw in self.urgence_keywords:
            kw_search = self._normalize_text(kw)
            if re.search(r'\b' + re.escape(kw_search) + r'\b', normalized_input):
                result['urgency'] = 'urgent'
                result['keywords'].append(kw)
                confidence_score += 0.2
                break
                
        # 3. Detect time preference
        for pref, keywords in self.time_preferences.items():
            for kw in keywords:
                kw_search = self._normalize_text(kw)
                if re.search(r'\b' + re.escape(kw_search) + r'\b', normalized_input):
                    result['time_preference'] = pref
                    result['keywords'].append(kw)
                    confidence_score += 0.2
                    break
                    
        # 4. Temporal parsing
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if re.search(r'\baujourd[\'’ ]?hui\b', normalized_input):
            result['date_min'] = today
            result['date_max'] = today + timedelta(days=1)
            confidence_score += 0.3
        elif re.search(r'\bdemain\b', normalized_input):
            result['date_min'] = today + timedelta(days=1)
            result['date_max'] = today + timedelta(days=2)
            confidence_score += 0.3
        elif re.search(r'\bapres[- ]demain\b', normalized_input):
            result['date_min'] = today + timedelta(days=2)
            result['date_max'] = today + timedelta(days=3)
            confidence_score += 0.3
        elif re.search(r'\bcette semaine\b', normalized_input):
            result['date_min'] = today
            result['date_max'] = today + timedelta(days=7)
            confidence_score += 0.3
        elif re.search(r'\bweek-?end\b', normalized_input):
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
            if re.search(r'\b' + day + r'\b', normalized_input):
                days_ahead = i - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                target_day = today + timedelta(days=days_ahead)
                result['date_min'] = target_day
                result['date_max'] = target_day + timedelta(days=1)
                confidence_score += 0.3
                break
                
        # Time parsing e.g. "entre 9h et 12h"
        time_match = re.search(r'entre (\d{1,2})h et (\d{1,2})h', normalized_input)
        if time_match:
            start_h = int(time_match.group(1))
            if start_h < 12:
                result['time_preference'] = 'morning'
            elif start_h < 18:
                result['time_preference'] = 'afternoon'
            else:
                result['time_preference'] = 'evening'
            confidence_score += 0.2
        elif re.search(r'apres (\d{1,2})h', normalized_input):
            start_h = int(re.search(r'apres (\d{1,2})h', normalized_input).group(1))
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
                
        # Normalize category name to match DB exactly
        CATEGORY_MAP = {
            'Plomberie':    'Plomberie',
            'Électricité':  'Électricité', 
            'Jardinage':    'Jardinage',
            'Ménage':       'Ménage',
            'Baby-sitting': 'Baby-sitting',
            'Déménagement': 'Déménagement',
            'Climatisation':'Climatisation',
            'Peinture':     'Peinture',
        }
        if result['service']:
            result['service'] = CATEGORY_MAP.get(result['service'], 
                                                  result['service'])
                
        return result

    def _fallback_llm_parse(self, text: str) -> dict:
        API_URL = "https://api.groq.com/openai/v1/chat/completions"
        api_key = getattr(settings, 'GROQ_API_KEY', None)
        logger.debug("Groq fallback parser called for text: %s", text)

        if not api_key:
            logger.error("Missing GROQ_API_KEY for NLP fallback parser.")
            return None
        
        prompt = (
            "Extrais le service, la date et l'urgence du texte suivant. "
            "Si l'utilisateur parle d'une maison sale, d'un appartement sale, de nettoyage, de lavage ou de rangement, "
            "mappe cela vers Ménage. "
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
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}]
            }
            
            resp = requests.post(API_URL, headers=headers, json=data, timeout=10)
            logger.debug("Groq response status=%s body=%s", resp.status_code, resp.text)
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                content = content.replace('```json', '').replace('```', '').strip()
                return json.loads(content)
            logger.error("Groq API request failed with status %s: %s", resp.status_code, resp.text)
        except Exception as exc:
            logger.exception("Groq fallback parser exception for text %s: %s", text, exc)
            
        return None
