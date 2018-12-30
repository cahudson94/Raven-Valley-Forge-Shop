"""Model setup for products."""
from django.db import models
from sorl.thumbnail import ImageField
from multiselectfield import MultiSelectField
from taggit.managers import TaggableManager
from django.contrib.auth.models import User

PUB_STATUS = (
    ('PB', 'public'),
    ('PV', 'private'),
)

LENGTHS = (
    ('4\"', '4\"'),
    ('5\"', '5\"'),
    ('6\"', '6\"'),
    ('7\"', '7\"'),
    ('8\"', '8\"'),
    ('9\"', '9\"'),
    ('10\"', '10\"'),
    ('11\"', '11\"'),
    ('12\"', '12\"'),
    ('13\"', '13\"'),
    ('14\"', '14\"'),
    ('15\"', '15\"'),
    ('16\"', '16\"'),
)

DIAMS = (
    ('1/8\"', '1/8\"'),
    ('1/4\"', '1/4\"'),
    ('3/8\"', '3/8\"'),
    ('1/2\"', '1/2\"'),
    ('5/8\"', '5/8\"'),
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
    creator = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                )
    description = models.TextField(default='')
    color = models.TextField(
        max_length=500,
        blank=True)
    extras = models.TextField(
        max_length=500,
        blank=True)
    catagories = TaggableManager(blank=True)
    shipping_length = models.DecimalField(null=True, max_digits=5,
                                          decimal_places=2)
    shipping_width = models.DecimalField(null=True, max_digits=5,
                                         decimal_places=2)
    shipping_height = models.DecimalField(null=True, max_digits=5,
                                          decimal_places=2)
    shipping_weight = models.DecimalField(null=True, max_digits=5,
                                          decimal_places=2)

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
    blurb = models.TextField(default='', blank=True)
    description = models.TextField(default='', blank=True)
    commission_fee = models.IntegerField(blank=True, default=0)
    price_range = models.CharField(
        max_length=15,
        default='',
        blank=True)
    limitations = models.TextField(max_length=500, default='', blank=True)
    extras = models.TextField(
        max_length=500,
        blank=True)
    warning = models.TextField(
        max_length=500,
        blank=True)

    def __str__(self):
        """Print for admin."""
        return self.name


class Discount(models.Model):
    """Model for discount codes."""

    code = models.CharField(max_length=30)
    code_type = models.CharField(max_length=20)
    value = models.CharField(max_length=10)
    code_state = models.BooleanField(default=True)
    description = models.CharField(max_length=250)
    prod = models.IntegerField(null=True, blank=True)
    prod_name = models.CharField(null=True, blank=True, max_length=30)


class UserServiceImage(models.Model):
    """Model to store images uploaded for a requested service."""

    image = ImageField(upload_to='service_images')
    used = models.BooleanField(default=False)

    def __str__(self):
        """Print for admin."""
        return str(self.id)
