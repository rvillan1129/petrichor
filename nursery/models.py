from django.db import models
from django.urls import reverse # Used in get_absolute_url() to get URL for specified ID
from django.db.models import UniqueConstraint # Constrains fields to unique values
from django.db.models.functions import Lower # Returns lower cased value of field

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
                name='common_name_case_insensitive_unique',
                violation_error_message = "Common name already exists (case insensitive match)"
            ),
        ]
