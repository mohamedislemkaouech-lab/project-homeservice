from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        null=True,
        blank=True
    )
    session_key = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Chat {self.pk} - {self.message[:50]}"


class FAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    keywords = models.CharField(max_length=500, help_text="Mots-clés séparés par des virgules")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
