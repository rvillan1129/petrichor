from django.shortcuts import render, get_object_or_404
from .models import Plant, PlantInstance, Location, CommonName
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime
from nursery.forms import RenewDueWateredDateForm, CreatePlantInstanceForm
from django.db.models import Q

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
    paginate_by = 10

class PlantDetailView(generic.DetailView):
    model = Plant

class PlantInstanceDetailView(generic.DetailView):
    model = PlantInstance

class LocationListView(generic.ListView):
    model = Location
    paginate_by = 2

class LocationDetailView(generic.DetailView):
    model = Location

class PlantInstanceByUserListView(LoginRequiredMixin,generic.ListView):
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
            .filter(due_watered__lte=datetime.date.today() )
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
            plant_instance.due_watered = form.cleaned_data['renewal_date']
            plant_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('my-plants'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=2)
        form = RenewDueWateredDateForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'plant_instance': plant_instance,
    }

    return render(request, 'nursery/renew_due_watered_date.html', context)
 

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
        
class PlantInstanceCreate(PermissionRequiredMixin, CreateView): 
    model = PlantInstance 
    fields = ['plant', 'customer', 'nickname', 'location', 'purchased', 'due_watered', 'status']
    proposed_due_watered_date = datetime.date.today() + datetime.timedelta(weeks=2) 
    initial = {'status': 'n', 
               'purchased': datetime.date.today(),
               'due_watered': proposed_due_watered_date}
    permission_required = 'nursery.add_plantinstance'

# @login_required
# @permission_required('nursery.add_plantinstance', raise_exception=True)
# this view should query data base for all instances created by user for provided nickname
# nickname should be unique per user, not per app
# def create_plant_instance(request, CreateView):
#     """View function for creating a new PlantInstance."""
#     # plant_instance = PlantInstance

#     # If this is a POST request then process the Form data
#     if request.method == 'POST':

#         # Create a form instance and populate it with data from the request (binding):
#         form = CreatePlantInstanceForm(request.POST)

#         # Check if the form is valid:
#         if form.is_valid():
#             # process the data in form.check_unique_nickname as required
#             plant_instance = form.check_unique_nickname_by_user
#             # plant_instance.save()

#             # redirect to a new URL:
#             return HttpResponseRedirect(reverse('my-plants'))

#     # If this is a GET (or any other method) create the default form.
#     else:
#         proposed_due_watered_date = datetime.date.today() + datetime.timedelta(weeks=2) 
#         form = CreatePlantInstanceFormForm(initial={'status': 'n', 
#                'purchased': datetime.date.today(),
#                'due_watered': proposed_due_watered_date})

#     context = {
#         'form': form,
#         'plant_instance': plant_instance,
#     }

#     return render(request, 'nursery/renew_due_watered_date.html', context)



class PlantInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = PlantInstance 
    fields = ['plant', 'customer', 'nickname', 'location', 'purchased', 'due_watered', 'status'] 
    permission_required = 'nursery.change_plantinstance' 

class PlantInstanceDelete(PermissionRequiredMixin, DeleteView): 
    model = PlantInstance 
    success_url = reverse_lazy('my-plants') 
    permission_required = 'nursery.delete_plantinstance' 
    
    def form_valid(self, form): 
        try: 
            self.object.delete() 
            return HttpResponseRedirect(self.success_url) 
        except Exception as e: 
            return HttpResponseRedirect( reverse("plant-instance-delete", kwargs={"pk": self.object.pk}) )