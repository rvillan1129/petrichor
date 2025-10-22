from django.contrib import admin
from .models import CommonName, Plant, PlantInstance, Location

#admin.site.register(CommonName)
#admin.site.register(Plant)
#admin.site.register(PlantInstance)
#admin.site.register(Location)

# Register the Admin classes for CommonName using the decorator
@admin.register(CommonName)
class CommonNameAdmin(admin.ModelAdmin):
    pass

# Register the Admin classes for Plant using the decorator
@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('scientific_name', 'display_common_name', 'water', 'sun', 'description', 'care_tips')
         

# Register the Admin classes for PlantInstance using the decorator
@admin.register(PlantInstance)
class PlantInstanceAdmin(admin.ModelAdmin):
    pass

# Register the Admin classes for Location using the decorator
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass