"""Model setup for services."""
from django.db import models
from sorl.thumbnail import ImageField
from taggit.managers import TaggableManager


PUB_STATUS = (
    ('PB', 'public'),
    ('PV', 'private'),
)


class Service(models.Model):
    """Service model for store display."""

    image = ImageField(upload_to='images')
    published = models.CharField(
        max_length=2,
        choices=PUB_STATUS,
        default='PV')
    date_created = models.DateTimeField(auto_now_add=True)
    date_published = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=100)
    decription = models.TextField(max_length=500, default='')
    limitations = models.TextField(max_length=500, default='')
    extras = models.TextField(
        max_length=500,
        blank=True)
    commision_fee = models.IntegerField(blank=True, default=0)
    price_range = models.CharField(
        max_length=15,
        default='')
    warning = models.TextField(
        max_length=500,
        blank=True)
    Tags = TaggableManager()

    def __str__(self):
        """Print for admin."""
        return self.name
