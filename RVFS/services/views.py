"""."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from services.models import Service
from services.forms import ServiceForm


class CreateServiceView(LoginRequiredMixin, CreateView):
    """View for creating black smith services."""

    template_name = 'create_service.html'
    model = Service
    success_url = reverse_lazy('home')
    form_class = ServiceForm
