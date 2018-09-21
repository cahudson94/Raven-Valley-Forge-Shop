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


class QuoteForm(forms.Form):
    """Form to contact shop."""

    names = []
    for serv in Service.objects.filter(published='PB'):
        names.append((serv.name, serv.name))
    first_name = forms.CharField(required=True, label="* First name")
    last_name = forms.CharField(required=True, label="* Last name")
    home_phone = forms.CharField(required=True, label="* Home phone")
    cell_phone = forms.CharField()
    service = forms.ChoiceField(choices=names, label="* Service")
    description = forms.CharField(
        widget=forms.Textarea
    )
    address = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()
    zip_code = forms.CharField(required=True, label="* Zip code")
    email = forms.EmailField(required=True, label="* Email")
    image_1 = forms.ImageField()
    image_2 = forms.ImageField()
    image_3 = forms.ImageField()
    image_4 = forms.ImageField()

    def __init__(self, *args, **kwargs):
        """."""
        super(QuoteForm, self).__init__(*args, **kwargs)
