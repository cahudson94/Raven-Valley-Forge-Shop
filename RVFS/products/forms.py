"""."""
from django import forms
from products.models import Product


class ProductForm(forms.ModelForm):
    """From for album create view."""

    class Meta:
        """Meta for ablum form."""

        model = Product
        exclude = ['date_created', 'date_published']
