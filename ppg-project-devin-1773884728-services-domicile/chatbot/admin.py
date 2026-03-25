from django.contrib import admin
from .models import ChatMessage, FAQ


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message', 'response')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'keywords', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer', 'keywords')
