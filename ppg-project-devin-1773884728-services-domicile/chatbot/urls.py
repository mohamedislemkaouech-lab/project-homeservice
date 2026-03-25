# chatbot/urls.py
# URL routing for the chatbot app.
# /chatbot/api/       -> original keyword-based bot (backward compat)
# /chatbot/api/chat/  -> Ollama-powered multi-turn chat (tinyllama)

from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.chat_api, name='chat_api'),
    path('api/chat/', views.ollama_chat_api, name='ollama_chat_api'),
]
