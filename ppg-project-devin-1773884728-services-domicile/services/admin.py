from django.contrib import admin
from .models import Category, Service, Availability


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'category', 'price', 'price_unit', 'city', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'city', 'price_unit')
    search_fields = ('title', 'description', 'provider__first_name', 'provider__last_name')


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('provider', 'day_of_week', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available')
