from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:reservation_pk>/', views.create_review, name='create_review'),
    path('<int:pk>/moderate/<str:action>/', views.moderate_review, name='moderate_review'),
]
