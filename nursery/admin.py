from django.contrib import admin
from .models import CommonName, Plant, PlantInstance, Location

admin.site.register(CommonName)
admin.site.register(Plant)
admin.site.register(PlantInstance)
admin.site.register(Location)
