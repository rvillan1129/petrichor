from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('plants/', views.PlantListView.as_view(), name='plants'),
    path('plant/<int:pk>', views.PlantDetailView.as_view(), name='plant-detail'),
]