"""."""
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from services.models import Service
from services.forms import ServiceForm


def index(request):
    """."""
    return HttpResponse("Hello, world. You're at the services.")


class CreateService(CreateView):
    """View for creating black smith services."""

    template_name = 'RVFS/create_service.html'
    model = Service
    success_url = reverse_lazy('home')
    form_class = ServiceForm
