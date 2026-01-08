from django.shortcuts import render, get_object_or_404
from .models import Plant, PlantInstance, Location, CommonName
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from nursery.forms import RenewDueWateredDateForm

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

class PlantsByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing watered plants by current user."""
    model = PlantInstance
    template_name = 'nursery/plantinstance_list_plants_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            PlantInstance.objects.filter(customer=self.request.user)
            .order_by('due_watered')
        )

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
    
class DueWateredPlantsByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing plants due watered by current user."""
    model = PlantInstance
    template_name = 'nursery/plantinstance_list_due_watered_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            PlantInstance.objects.filter(customer=self.request.user)
            .filter(status__exact='n')
            .order_by('due_watered')
        )

@login_required
def renew_due_watered_date(request, pk):
    """View function for renewing due watered date for a specific PlantInstance."""
    plant_instance = get_object_or_404(PlantInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewDueWateredDateForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_watered field)
            plant_instance.due_back = form.cleaned_data['renewal_date']
            plant_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('my-watered'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=2)
        form = RenewDueWateredDateForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'plant_instance': plant_instance,
    }

    return render(request, 'nursery/renew_due_watered_date.html', context)

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin 
from django.urls import reverse_lazy 
from .models import Plant 

class PlantCreate(PermissionRequiredMixin, CreateView): 
    model = Plant 
    fields = ['scientific_name', 'common_name', 'water', 'sun', 'description', 'care_tips'] 
    initial = {'water': 'r', 'sun': 'p'}
    permission_required = 'nursery.add_plant'

class PlantUpdate(PermissionRequiredMixin, UpdateView): 
    model = Plant 
    # Not recommended (potential security issue if more fields added) 
    fields = '__all__' 
    permission_required = 'nursery.change_plant' 
    
class PlantDelete(PermissionRequiredMixin, DeleteView): 
    model = Plant 
    success_url = reverse_lazy('plants') 
    permission_required = 'nursery.delete_plant' 
    
    def form_valid(self, form): 
        try: 
            self.object.delete() 
            return HttpResponseRedirect(self.success_url) 
        except Exception as e: 
            return HttpResponseRedirect( reverse("plant-delete", kwargs={"pk": self.object.pk}) )