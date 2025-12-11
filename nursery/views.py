from django.shortcuts import render
from .models import Plant, PlantInstance, Location, CommonName
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_plants = Plant.objects.all().count()
    num_instances = PlantInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_purchased = PlantInstance.objects.filter(status__exact='p').count()

    # The 'all()' is implied by default.
    num_locations = Location.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    context = {
        'num_plants': num_plants,
        'num_instances': num_instances,
        'num_instances_purchased': num_instances_purchased,
        'num_locations': num_locations,
        'num_visits': num_visits,
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

class WateredPlantsByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing watered plants by current user."""
    model = PlantInstance
    template_name = 'nursery/plantinstance_list_watered_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            PlantInstance.objects.filter(customer=self.request.user)
            .filter(status__exact='w')
            .order_by('due_watered')
        )