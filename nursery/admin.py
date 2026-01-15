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

class PlantInstanceInline(admin.StackedInline):
    model = PlantInstance
    extra = 0
    fields = ['nickname', 'location', ('purchased', 'due_watered'), 'status', 'id']
    readonly_fields = ['nickname', 'location', 'purchased', 'due_watered', 'status', 'id']

# Register the Admin classes for Plant using the decorator
@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('scientific_name', 'common_name', 'water', 'sun', 'description', 'care_tips', 'user')

    fields = ['user', ('scientific_name', 'common_name'), ('water', 'sun'), 'description', 'care_tips']

    inlines = [PlantInstanceInline]

# Register the Admin classes for PlantInstance using the decorator
@admin.register(PlantInstance)
class PlantInstanceAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'plant', 'customer','location', 'status', 'due_watered')
    list_filter = ('status', 'due_watered')

    fields = ['plant', 'nickname', 'location', 'customer', ('purchased', 'due_watered'), 'status', 'id']
    readonly_fields = ['id']

# Register the Admin classes for Location using the decorator
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass