"""."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from catalog.models import Product, Service
from catalog.forms import ProductForm, ServiceForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class CatalogView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'shop-home.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        context['products'] = context['product_list'].filter(published='PB')
        context['services'] = Service.objects.filter(published='PB')
        context['prod_tags'] = sorted(set([tag for prod in context['products'] for tag in prod.tags.names()]))
        context['serv_tags'] = sorted(set([tag for serv in context['services'] for tag in serv.tags.names()]))
        context['nbar'] = 'cata'
        return context


class AllProductsView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'catalog.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        products = context['product_list'].filter(published='PB')
        context['tags'] = sorted(set([tag for prod in products for tag in prod.tags.names()]))
        context['items'] = {tag: [prod for prod in products if tag in prod.tags.names()] for tag in context['tags']}
        context['nbar'] = 'prods'
        return context


class AllServicesView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'catalog.html'
    model = Service

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        services = Service.objects.filter(published='PB')
        context['tags'] = sorted(set([tag for serv in services for tag in serv.tags.names()]))
        context['items'] = {tag: [serv for serv in services if tag in serv.tags.names()] for tag in context['tags']}
        context['nbar'] = 'servs'
        return context


class TagProductsView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'tagged_catalog.html'
    model = Product

    def get_queryset(self):
        """Filter for the tag."""
        return(Product.objects.filter(published='PB')
                              .filter(tags__slug=[self.kwargs.get('slug')]).all())

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(TagProductsView, self).get_context_data(**kwargs)
        tag = self.kwargs.get('slug')
        context['tag'] = tag
        products = (Product.objects.filter(published='PB')
                                   .filter(tags__name__in=[self.kwargs.get('slug')]).all())
        paginator = Paginator(products, 20)
        page = context['view'].request.GET.get('page')
        try:
            context['items'] = paginator.page(page)
        except PageNotAnInteger:
            context['items'] = paginator.page(1)
        except EmptyPage:
            context['items'] = paginator.page(paginator.num_pages)
        context['nbar'] = 'prods'
        context['tags'] = sorted(set([tag for prod in context['items'] for tag in prod.tags.names()]))
        return context


class TagServicesView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'tagged_catalog.html'
    model = Service

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        services = context['service_list'].filter(published='PB', tag__slug=kwargs['slug'])
        paginator = Paginator(services, 20)
        page = context['view'].request.GET.get('page')
        try:
            context['items'] = paginator.page(page)
        except PageNotAnInteger:
            context['items'] = paginator.page(1)
        except EmptyPage:
            context['items'] = paginator.page(paginator.num_pages)
        context['nbar'] = 'servs'
        context['tags'] = sorted(set([tag for serv in context['items'] for tag in serv.tags.names()]))
        return context


class SingleProductView(DetailView):
    """Detail view for a product."""

    template_name = 'product.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(DetailView, self).get_context_data(**kwargs)
        context['nbar'] = 'prods'
        return context


class CreateProductView(PermissionRequiredMixin, CreateView):
    """View for creating a product."""

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

    def form_valid(self, form):
        """Update date published."""
        form.save()
        import pdb; pdb.set_trace()
        if form['published'] == 'PB':
            pass


class EditProductView(PermissionRequiredMixin, UpdateView):
    """View for editing a product."""

    permission_required = 'user.is_staff'
    template_name = 'edit_product.html'
    model = Product
    form_class = ProductForm

    # def get_success_url(self):
    #     """Redirect to detail page."""


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
