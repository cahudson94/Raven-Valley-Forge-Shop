"""."""
from django.contrib import admin
from catalog.models import Product, Service, SliderImage

admin.site.register(Product)
admin.site.register(Service)
admin.site.register(SliderImage)
