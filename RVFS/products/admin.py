"""."""
from django.contrib import admin
from products.models import Product, SliderImage

admin.site.register(Product)
admin.site.register(SliderImage)
