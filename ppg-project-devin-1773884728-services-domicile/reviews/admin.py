from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('client', 'reservation', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('client__first_name', 'comment')
