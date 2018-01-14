"""."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from services.models import Service
from services.forms import ServiceForm


class CreateServiceView(PermissionRequiredMixin, CreateView):
    """View for creating black smith services."""

    permission_required = 'user.is_staff'
    template_name = 'create_service.html'
    model = Service
    success_url = reverse_lazy('home')
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CreateView, self).get_context_data(**kwargs)
        context['nbar'] = 'add_serv'
        return context
