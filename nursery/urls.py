from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('plants/', views.PlantListView.as_view(), name='plants'),
    path('plant/<int:pk>', views.PlantDetailView.as_view(), name='plant-detail'),
    path('plantinstances/', views.PlantInstanceStaffOnlyListView.as_view(), name='plantinstances'),
    path('plantinstance/<uuid:pk>', views.PlantInstanceDetailView.as_view(), name='plant-instance-detail'),
    path('locations/', views.LocationListView.as_view(), name='locations'),
    path('mylocations/', views.LocationByUserListView.as_view(), name='my-locations'),
    path('location/<int:pk>', views.LocationDetailView.as_view(), name='location-detail'),
]

urlpatterns += [
    path('myplanttemplates/', views.PlantByUserListView.as_view(), name='user-plant-templates'),
    path('myplants/', views.PlantInstanceByUserListView.as_view(), name='my-plants'),
    path('myduewateredplants/', views.DueWateredPlantsByUserListView.as_view(), name='my-due-watered'),
]

urlpatterns += [
    path('plant/<uuid:pk>/renew_due_watered/', views.renew_due_watered_date, name='renew-due-watered-date'),
]

urlpatterns += [ 
    path('plant/create/', views.PlantCreate.as_view(), name='plant-create'), 
    path('plant/<int:pk>/update/', views.PlantUpdate.as_view(), name='plant-update'), 
    path('plant/<int:pk>/delete/', views.PlantDelete.as_view(), name='plant-delete'),
    path('location/create/', views.LocationCreate.as_view(), name='location-create'),
    path('location/<int:pk>/update/', views.LocationUpdate.as_view(), name='location-update'), 
    path('location/<int:pk>/delete/', views.LocationDelete.as_view(), name='location-delete'),]

urlpatterns += [ 
    path('plantinstance/create/', views.PlantInstanceCreate.as_view(), name='plant-instance-create'),
    path('plantinstance/<int:pk>/create/', views.PlantInstanceCreateFromPlant.as_view(), name='plant-instance-create-from-plant'),
    path('plantinstanceloc/<int:pk>/create/', views.PlantInstanceCreateFromLocation.as_view(), name='plant-instance-create-from-location'),
    path('plantinstance/<uuid:pk>/update/', views.PlantInstanceUpdate.as_view(), name='plant-instance-update'), 
    path('plantinstance/<uuid:pk>/delete/', views.PlantInstanceDelete.as_view(), name='plant-instance-delete'),]

urlpatterns += [
    path('staff/location/<int:pk>/update/', views.LocationUpdateStaffOnly.as_view(), name='staff-location-update'),
    path('staff/plant/<int:pk>/update/', views.PlantUpdateStaffOnly.as_view(), name='staff-plant-update'),
    path('staff/plantinstance/<uuid:pk>/update/', views.PlantInstanceUpdateStaffOnly.as_view(), name='staff-plant-instance-update'), 
]