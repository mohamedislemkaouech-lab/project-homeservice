from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:service_pk>/', views.create_reservation, name='create_reservation'),
    path('my/', views.my_reservations, name='my_reservations'),
    path('<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('<int:pk>/status/<str:status>/', views.update_reservation_status, name='update_reservation_status'),
    path('<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
]
