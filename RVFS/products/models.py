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
    decription = models.TextField(default='')
    price = models.DecimalField(null=True, max_digits=6, decimal_places=2)
    stock = models.IntegerField(null=True, blank=True)
    shipping_info = models.TextField(
        max_length=180,
        blank=True)
    length = MultiSelectField(
        max_length=150,
        choices=LENGTHS,
        default='',
        blank=True)
    diamiter = MultiSelectField(
        max_length=150,
        choices=DIAMS,
        default='',
        blank=True)
    color = models.TextField(
        max_length=500,
        blank=True)
    extra_options = models.TextField(
        max_length=500,
        blank=True)
    Tags = TaggableManager()

    def __str__(self):
        """Print for admin."""
        return self.name


class SliderImages(models.Model):
    """Image model for home page slider."""

    photo = ImageField(upload_to='slides')
    date_added = models.DateTimeField(auto_now_add=True)
    title = models.CharField(default='', max_length=50)

    def __str__(self):
        """Print for admin."""
        return self.title
