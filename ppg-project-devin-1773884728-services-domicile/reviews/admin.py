from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client', 'reservation', 'rating', 'is_visible', 'created_at')
    list_filter = ('rating', 'is_visible')
    search_fields = ('client__first_name', 'comment')
    list_editable = ('is_visible',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('client', 'reservation', 'rating')
        }),
        ('Détails de l\'avis', {
            'fields': ('rating_punctuality', 'rating_quality', 'rating_communication', 'rating_value', 'comment')
        }),
        ('Modération', {
            'fields': ('is_visible', 'moderation_note')
        }),
        ('Métadonnées', {
            'fields': ('created_at',)
        })
    )
