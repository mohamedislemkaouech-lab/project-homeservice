from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'client', 'service', 'date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('client__first_name', 'client__last_name', 'service__title')
