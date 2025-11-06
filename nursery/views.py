from django.shortcuts import render
from .models import Plant, PlantInstance, Location, CommonName
from django.views import generic

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_plants = Plant.objects.all().count()
    num_instances = PlantInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_purchased = PlantInstance.objects.filter(status__exact='p').count()

    # The 'all()' is implied by default.
    num_locations = Location.objects.count()

    context = {
        'num_plants': num_plants,
        'num_instances': num_instances,
        'num_instances_purchased': num_instances_purchased,
        'num_locations': num_locations,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class PlantListView(generic.ListView):
    model = Plant
    paginate_by = 2

class PlantDetailView(generic.DetailView):
    model = Plant

class LocationListView(generic.ListView):
    model = Location
    paginate_by = 2

class LocationDetailView(generic.DetailView):
    model = Location