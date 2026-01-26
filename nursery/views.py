from django.shortcuts import render, get_object_or_404, Http404
from .models import Plant, PlantInstance, Location
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime
from nursery.forms import RenewDueWateredDateForm
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
    num_users = User.objects.count()

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
        'num_users': num_users,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class PlantListView(UserPassesTestMixin, generic.ListView):
    """Generic class-based view listing all plants if user is staff."""
    model = Plant
    paginate_by = 10

    def test_func(self):
        # test if user is staff
        return self.request.user.is_staff

class PlantByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing plants by current user."""
    model = Plant
    template_name = 'nursery/plant_list_by_user_and_groundskeep.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            Plant.objects.filter(user=self.request.user)
            .order_by('scientific_name')
        )

class PlantDetailView(generic.DetailView):
    model = Plant

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        
        # Add in a QuerySet of all related plant instances for this user
        # self.object refers to the publisher instance retrieved by DetailView
        context["plantinstance_list"] = PlantInstance.objects.filter(customer=self.object.user).filter(plant=self.object)
        
        return context


class LocationListView(UserPassesTestMixin, generic.ListView):
    """Generic class-based view listing all locations if user is staff."""
    model = Location
    paginate_by = 10

    def test_func(self):
        # test if user is staff
        return self.request.user.is_staff
    
class LocationByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing locations by current user."""
    model = Location
    template_name = 'nursery/location_list_by_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            Location.objects.filter(user=self.request.user)
            .order_by('name')
        )

class LocationDetailView(generic.DetailView):
    model = Location

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        
        # Add in a QuerySet of all related plant instances for this user
        # self.object refers to the publisher instance retrieved by DetailView
        context["plantinstance_list"] = PlantInstance.objects.filter(customer=self.object.user).filter(location=self.object)
        
        return context


class PlantInstanceStaffOnlyListView(UserPassesTestMixin, generic.ListView):
    """Generic class-based view listing all plant instances if user is staff."""
    model = PlantInstance
    template_name = 'nursery/plantinstance_list_staff_only.html'
    paginate_by = 10

    def test_func(self):
        # test if user is staff
        return self.request.user.is_staff

class PlantInstanceDetailView(generic.DetailView):
    model = PlantInstance

class PlantInstanceByUserListView(LoginRequiredMixin, generic.ListView):
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
            plant_instance.status = 'w'
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
 
## ***** CRUD Operations ***** ##

class PlantCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView): 
    model = Plant 
    fields = ['scientific_name', 'common_name','water', 'sun', 'description', 'care_tips'] 
    initial = {'water': 'r', 'sun': 'p',}
    permission_required = 'nursery.add_plant'

    def form_valid(self, form):
        # set Plant user equal to user creating plant
        form.instance.user = self.request.user
        return super().form_valid(form)

class PlantUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView): 
    model = Plant 
    fields = ['scientific_name', 'common_name','water', 'sun', 'description', 'care_tips'] 
    permission_required = 'nursery.change_plant'
    
    def get_queryset(self):
        # Start with the base queryset
        queryset = super().get_queryset()
        # Further filter the queryset to include only objects created by the current user
        return queryset.filter(user=self.request.user)

class PlantUpdateStaffOnly(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Plant
    fields = ['scientific_name', 'user', 'common_name','water', 'sun', 'description', 'care_tips'] 
    permission_required = 'nursery.change_plant'


    def test_func(self):
        # test if user is staff
        return self.request.user.is_staff

class PlantDelete(PermissionRequiredMixin, DeleteView): 
    model = Plant 
    success_url = reverse_lazy('user-plant-templates')  
    permission_required = 'nursery.delete_plant' 
    
    def form_valid(self, form): 
        try: 
            obj = self.object
            
            if self.request.user.is_staff:
                obj.delete() 
                return HttpResponseRedirect(reverse_lazy('plants')) 
            elif obj.user == self.request.user:
                obj.delete() 
                return HttpResponseRedirect(self.success_url) 
            else:
                messages.error(self.request, "Error: You are not allowed to delete this plant.")
                return HttpResponseRedirect( reverse("plant-delete", kwargs={"pk": self.object.pk}) )
        except Exception as e: 
            return HttpResponseRedirect( reverse("plant-delete", kwargs={"pk": self.object.pk}) )


class PlantInstanceCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView): 
    model = PlantInstance 
    fields = ['plant', 'nickname', 'location', 'purchased', 'due_watered', 'status']
    proposed_due_watered_date = datetime.date.today() + datetime.timedelta(weeks=2) 
    initial = {'status': 'w', 
               'purchased': datetime.date.today(),
               'due_watered': proposed_due_watered_date}
    permission_required = 'nursery.add_plantinstance'

    # filter queryset for plant drop-down by user or staff
    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        # if user is staff don't filter queryset and just return
        if self.request.user.is_staff:
            return form
        else:
            form.fields['plant'].queryset = form.fields['plant'].queryset.filter(user=self.request.user)
            form.fields['location'].queryset = form.fields['location'].queryset.filter(user=self.request.user)
        return form

    # This shows up after form submission, in definition
    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)

class PlantInstanceCreateFromPlant(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = PlantInstance 
    fields = ['plant', 'nickname', 'location', 'purchased', 'due_watered', 'status']
    permission_required = 'nursery.add_plantinstance'

    # filter queryset for plant drop-down by user or staff
    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        if self.request.user.is_staff:
            return form
        else:
            form.fields['plant'].queryset = form.fields['plant'].queryset.filter(user=self.request.user)
            form.fields['location'].queryset = form.fields['location'].queryset.filter(user=self.request.user)
        return form
    
    # Set the initial value for a specific field
    # The value should be the primary key or the actual object instance if it's a ForeignKey/ModelChoiceField
    # This shows up before form submission
    def get_initial(self):
        # Retrieve plant object using the pk from the URL
        plant = get_object_or_404(Plant, pk=self.kwargs['pk'])
        proposed_due_watered_date = datetime.date.today() + datetime.timedelta(weeks=2)
        initial = super().get_initial()

        initial['status'] = 'w'
        initial['purchased'] = datetime.date.today()
        initial['due_watered'] = proposed_due_watered_date
        initial['plant'] = plant

        return initial
    
    # This shows up after form submission, in definition
    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)
    
class PlantInstanceCreateFromLocation(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = PlantInstance 
    fields = ['plant', 'nickname', 'location', 'purchased', 'due_watered', 'status']
    permission_required = 'nursery.add_plantinstance'

    # filter queryset for plant drop-down by user or staff
    def get_form(self, form_class=None):
        form = super().get_form(form_class=None)
        if self.request.user.is_staff:
            return form
        else:
            form.fields['plant'].queryset = form.fields['plant'].queryset.filter(user=self.request.user)
            form.fields['location'].queryset = form.fields['location'].queryset.filter(user=self.request.user)
        return form
    
    # Set the initial value for a specific field
    # The value should be the primary key or the actual object instance if it's a ForeignKey/ModelChoiceField
    # This shows up before form submission
    def get_initial(self):
        # Retrieve location object using the pk from the URL
        location = get_object_or_404(Location, pk=self.kwargs['pk'])
        proposed_due_watered_date = datetime.date.today() + datetime.timedelta(weeks=2)
        initial = super().get_initial()

        initial['status'] = 'w'
        initial['purchased'] = datetime.date.today()
        initial['due_watered'] = proposed_due_watered_date
        initial['location'] = location

        return initial
    
    # This shows up after form submission, in definition
    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)

class PlantInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = PlantInstance 
    fields = ['plant', 'nickname', 'location', 'purchased', 'due_watered', 'status'] 
    permission_required = 'nursery.change_plantinstance' 

    def get_queryset(self):
        # Start with the base queryset
        queryset = super().get_queryset()
        # Further filter the queryset to include only objects created by the current user
        return queryset.filter(customer=self.request.user)

class PlantInstanceUpdateStaffOnly(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PlantInstance 
    fields = ['plant', 'customer', 'nickname', 'location', 'purchased', 'due_watered', 'status'] 
    permission_required = 'nursery.change_plantinstance' 

    def test_func(self):
        # test if user is staff
        return self.request.user.is_staff

class PlantInstanceDelete(PermissionRequiredMixin, DeleteView): 
    model = PlantInstance 
    success_url = reverse_lazy('my-plants') 
    permission_required = 'nursery.delete_plantinstance' 
    
    def form_valid(self, form): 
        try: 
            obj = self.object

            if self.request.user.is_staff:
                obj.delete() 
                return HttpResponseRedirect(reverse_lazy('plantinstances')) 
            elif obj.customer == self.request.user:
                obj.delete() 
                return HttpResponseRedirect(self.success_url) 
            else:
                messages.error(self.request, "Error: You are not allowed to delete this plant instance.")
                return HttpResponseRedirect( reverse("plant-instance-delete", kwargs={"pk": self.object.pk}) )
        except Exception as e: 
            return HttpResponseRedirect( reverse("plant-instance-delete", kwargs={"pk": self.object.pk}) )
        
class LocationCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView): 
    model = Location 
    fields = ['name',] 
    permission_required = 'nursery.add_location'

    def form_valid(self, form):
        # set Location user equal to user creating location
        form.instance.user = self.request.user
        return super().form_valid(form)