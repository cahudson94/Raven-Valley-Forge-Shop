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

    subject = forms.CharField(required=True)
    from_email = forms.EmailField(required=True)
    message = forms.CharField(
        required=True,
        widget=forms.Textarea
    )

    def __init__(self, *args, **kwargs):
        """."""
        super(QuoteForm, self).__init__(*args, **kwargs)
        self.fields['subject'].label = "Your name:"
        self.fields['from_email'].label = "Your email:"
        self.fields['message'].label = "What can we help you with?"
