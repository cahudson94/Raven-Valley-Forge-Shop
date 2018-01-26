"""Model setup for products."""
from django.db import models
from sorl.thumbnail import ImageField
from multiselectfield import MultiSelectField
from taggit.managers import TaggableManager


PUB_STATUS = (
    ('PB', 'public'),
    ('PV', 'private'),
)

LENGTHS = (
    ('4', 4),
    ('5', 5),
    ('6', 6),
    ('7', 7),
    ('8', 8),
    ('9', 9),
    ('10', 10),
    ('11', 11),
    ('12', 12),
    ('13', 13),
    ('14', 14),
    ('15', 15),
    ('16', 16),
)

DIAMS = (
    ('1/8', '1/8'),
    ('1/4', '1/4'),
    ('3/8', '3/8'),
    ('1/2', '1/2'),
    ('5/8', '5/8'),
)


class Product(models.Model):
    """Product model for store display."""

    image = ImageField(upload_to='images')
    published = models.CharField(
        max_length=2,
        choices=PUB_STATUS,
        default='PV')
    date_created = models.DateTimeField(auto_now_add=True)
    date_published = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    stock = models.IntegerField(null=True, blank=True)
    tags = TaggableManager()
    length = MultiSelectField(
        max_length=150,
        choices=LENGTHS,
        default='',
        blank=True)
    diameter = MultiSelectField(
        max_length=150,
        choices=DIAMS,
        default='',
        blank=True)
    is_knife = models.BooleanField(default=False)
    description = models.TextField(default='')
    color = models.TextField(
        max_length=500,
        blank=True)
    extras = models.TextField(
        max_length=500,
        blank=True)

    def __str__(self):
        """Print for admin."""
        return self.name


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
    description = models.TextField(max_length=500, default='')
    is_knife = models.BooleanField(default=False)
    requires_pictures = models.BooleanField(default=False)
    requires_description = models.BooleanField(default=False)
    requires_address = models.BooleanField(default=False)
    commission_fee = models.IntegerField(blank=True, default=0)
    price_range = models.CharField(
        max_length=15,
        default='')
    limitations = models.TextField(max_length=500, default='')
    extras = models.TextField(
        max_length=500,
        blank=True)
    warning = models.TextField(
        max_length=500,
        blank=True)
    tags = TaggableManager()

    def __str__(self):
        """Print for admin."""
        return self.name
