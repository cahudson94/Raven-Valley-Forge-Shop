from django import forms
from services.models import Service


class ServiceForm(forms.ModelForm):
    """From for album create view."""

    class Meta:
        """Meta for ablum form."""

        model = Service
        exlude = ['date_created']
