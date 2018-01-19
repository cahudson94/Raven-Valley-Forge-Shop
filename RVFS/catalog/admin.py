"""."""
from django.contrib import admin
from catalog.models import Product, Service

admin.site.register(Product)
admin.site.register(Service)
