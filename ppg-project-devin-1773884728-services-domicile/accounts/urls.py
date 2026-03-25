from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_choice, name='register_choice'),
    path('register/client/', views.register_client, name='register_client'),
    path('register/prestataire/', views.register_prestataire, name='register_prestataire'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('provider/<int:pk>/', views.provider_profile, name='provider_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
