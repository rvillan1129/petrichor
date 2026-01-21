from django.db import models
from django.urls import reverse # Used in get_absolute_url() to get URL for specified ID
from django.db.models import UniqueConstraint # Constrains fields to unique values
from django.db.models.functions import Lower # Returns lower cased value of field
import uuid # Required for unique plant instances
from django.conf import settings
from django.contrib.auth.models import User
from datetime import date

class CommonName(models.Model):
    """Model representing a plant common name."""
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter common name (e.g. Spider Plant, Snake Plant)"
    )

    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular common name instance."""
        return reverse('commonName-detail', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='commonName_name_case_insensitive_unique',
                violation_error_message = "Common name already exists (case insensitive match)"
            ),
        ]

class Plant(models.Model):
    """Model representing a type of plant."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    scientific_name = models.CharField(max_length=200)
    common_name = models.CharField(max_length=200, help_text="Select a common name for this plant", null=True)
    
    WATER_FREQ = (
        ('f', 'frequent'),
        ('r', 'regular'),
        ('i', 'infrequent'),
    )

    SUN = (
        ('f', 'full sun'),
        ('fp', 'full sun to part shade'),
        ('p', 'part shade'),
        ('ps', 'part shade to full shade'),
        ('sh', 'full shade'),
    )

    water = models.CharField(
        max_length=1,
        choices=WATER_FREQ,
        blank=False,
        help_text='watering frequency',
    )
    sun = models.CharField(
        max_length=2,
        choices=SUN,
        blank=False,
        help_text='sun light preference',
    )

    #image = models.ImageField(upload_to='Plants')

    description = models.TextField(max_length=1000, help_text="Enter a brief description of the plant")
    
    care_tips = models.TextField(max_length=1000, help_text="Enter a few care tips for the plant")

    class Meta:
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(fields=['user', 'scientific_name'], name='unique_plant_scientificname_per_owner')
        ]

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.scientific_name}'

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this plant."""
        return reverse('plant-detail', args=[str(self.id)])

class PlantInstance(models.Model):
    """Model representing an instance of a type of plant."""
    plant = models.ForeignKey(Plant, on_delete=models.RESTRICT, null=True)
    ## change to owner
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nickname = models.CharField(max_length=200, help_text='what do you call your plant child')
    
    # Foreign Key used because plant can only have one location, but location can house multiple plants.
    # location as a string rather than object because it hasn't been declared yet in file.
    location = models.ForeignKey('Location', on_delete=models.RESTRICT, null=True, help_text='location plant will live')
    
    purchased = models.DateField(null=True, blank=True, help_text='date plant was purchase')
    due_watered = models.DateField(null=True, blank=True, help_text='next watering date')

    WATERED_STATUS = (
        ('w', 'watered'),
        ('n', 'not watered'),
    )

    status = models.CharField(
        max_length=1,
        choices=WATERED_STATUS,
        blank=True,
        default='w',
        help_text='plant watered status',
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular plant across whole nursery")
    
    @property
    def is_overdue_watered(self):
        """Determines if the plant is overdue to be watered on due date and current date."""

        return bool(self.due_watered and (date.today() >= self.due_watered))

    @property
    def is_not_watered(self):
        """Determines if the plant has not been watered."""

        return bool(self.status and (self.status == 'n'))

    class Meta:
        ordering = ['customer','nickname']
        constraints = [
            models.UniqueConstraint(fields=['customer', 'nickname'], name='unique_plantinstance_nickname_per_customer')
        ]

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.nickname} ({self.plant.scientific_name}) {self.id}'
    
    def display_common_name(self):
        """Create a string for common_name. This is required to display common_name in Admin."""
        return self.plant.common_name
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this plant instance"""
        return reverse('plant-instance-detail', args=[str(self.id)])

    display_common_name.short_description = 'Common Name'
    
class Location(models.Model):
    """Model representing a Location (e.g. Living Room, Kitchen, etc.)"""
    name = models.CharField(max_length=50,
                            unique=True,
                            help_text="Enter the plant's Location (e.g. Living Room, Kitchen, etc.)")

    def get_absolute_url(self):
        """Returns the url to access a particular location instance."""
        return reverse('location-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='location_name_case_insensitive_unique',
                violation_error_message = "Location already exists (case insensitive match)"
            ),
        ]
