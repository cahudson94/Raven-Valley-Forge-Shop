"""."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from products.models import Product
from products.forms import ProductForm


class CreateProductView(PermissionRequiredMixin, CreateView):
    """View for creating black smith services."""

    permission_required = 'user.is_staff'
    template_name = 'create_product.html'
    model = Product
    success_url = reverse_lazy('home')
    form_class = ProductForm

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CreateView, self).get_context_data(**kwargs)
        context['nbar'] = 'add_prod'
        return context
