# chatbot/urls.py
# Wire /chatbot/api/chat/ to the Ollama proxy view.

from django.urls import path
from . import views

urlpatterns = [
    path("api/chat/", views.SearchAPIView.as_view(), name="chat_api"),
]
