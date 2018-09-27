"""."""
from django import forms
from catalog.models import Product, Service


class ProductForm(forms.ModelForm):
    """From for album create view."""

    class Meta:
        """Meta for ablum form."""

        model = Product
        exclude = ['date_created', 'date_published']


class ServiceForm(forms.ModelForm):
    """From for album create view."""

    class Meta:
        """Meta for ablum form."""

        model = Service
        exclude = ['date_created', 'date_published']
