from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('plants/', views.PlantListView.as_view(), name='plants'),
    path('plant/<int:pk>', views.PlantDetailView.as_view(), name='plant-detail'),
    path('locations/', views.LocationListView.as_view(), name='locations'),
    path('location/<int:pk>', views.LocationDetailView.as_view(), name='location-detail'),
]

urlpatterns += [
    path('myplants/', views.WateredPlantsByUserListView.as_view(), name='my-watered'),
]

urlpatterns += [
    path('plant/<uuid:pk>/renew_due_watered/', views.renew_due_watered_date, name='renew-due-watered-date'),
]