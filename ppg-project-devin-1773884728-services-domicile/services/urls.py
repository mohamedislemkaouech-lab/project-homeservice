from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('category/<int:pk>/', views.category_services, name='category_services'),
    path('category/<int:pk>/api/', views.category_api, name='category_api'),
    path('category/<int:pk>/prestataires/', views.category_prestataires, name='category_prestataires'),
    path('create/', views.service_create, name='service_create'),
    path('<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('availability/', views.manage_availability, name='manage_availability'),
    path('availability/<int:pk>/delete/', views.delete_availability, name='delete_availability'),
]
