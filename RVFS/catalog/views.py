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
        products = Product.objects.filter(published='PB')
        services = Service.objects.filter(published='PB')
        context['prod_tags'] = sorted(set([tag for prod in products for tag in prod.tags.names()]))
        context['serv_tags'] = sorted(set([tag for serv in services for tag in serv.tags.names()]))
        context['all_tags'] = sorted(set(context['prod_tags'] + context['serv_tags']))
        prod_paginator = Paginator(context['prod_tags'], 3)
        serv_paginator = Paginator(context['serv_tags'], 3)
        request = context['view'].request
        if 'prod_page' in request.GET:
            prod_page = request.GET.get('prod_page').split('?serv_page')[0]
            serv_page = request.GET.get('prod_page').split('?serv_page')[1]
        else:
            prod_page = 1
            serv_page = 1
        try:
            context['prod_tags'] = prod_paginator.page(prod_page)
        except PageNotAnInteger:
            context['prod_tags'] = prod_paginator.page(1)
        except EmptyPage:
            context['prod_tags'] = prod_paginator.page(prod_paginator.num_pages)
        try:
            context['serv_tags'] = serv_paginator.page(serv_page)
        except PageNotAnInteger:
            context['serv_tags'] = serv_paginator.page(1)
        except EmptyPage:
            context['serv_tags'] = serv_paginator.page(serv_paginator.num_pages)
        context['products'] = {tag: [prod for prod in products if tag in prod.tags.names()] for tag in context['prod_tags']}
        context['services'] = {tag: [serv for serv in services if tag in serv.tags.names()] for tag in context['serv_tags']}
        context['nbar'] = 'cata'
        return context


class AllProductsView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'catalog.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        items = self.model.objects.filter(published='PB')
        context['all_tags'] = sorted(set([tag for item in items for tag in item.tags.names()]))
        paginator = Paginator(context['all_tags'], 5)
        request = context['view'].request
        if 'page' in request.GET:
            page = context['view'].request.GET.get('page')
        else:
            page = 1
        try:
            context['tags'] = paginator.page(page)
        except PageNotAnInteger:
            context['tags'] = paginator.page(1)
        except EmptyPage:
            context['tags'] = paginator.page(paginator.num_pages)
        context['items'] = {tag: [item for item in items if tag in item.tags.names()] for tag in context['tags']}
        context['nbar'] = 'prods'
        return context


class AllServicesView(AllProductsView):
    """Catalogue view for the shop of all products and services."""

    model = Service

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(AllProductsView, self).get_context_data(**kwargs)
        context['nbar'] = 'servs'
        return context


class TagProductsView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'tagged_catalog.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(TagProductsView, self).get_context_data(**kwargs)
        page_tag = self.kwargs.get('slug')
        context['tag'] = page_tag
        all_items = self.model.objects.filter(published='PB')
        context['all_tags'] = sorted(set([tag for item in all_items for tag in item.tags.names()]))
        items = (self.model.objects.filter(published='PB')
                                   .filter(tags__name__in=[self.kwargs.get('slug')]).all())
        paginator = Paginator(items, 20)
        page = context['view'].request.GET.get('page')
        try:
            context['items'] = paginator.page(page)
        except PageNotAnInteger:
            context['items'] = paginator.page(1)
        except EmptyPage:
            context['items'] = paginator.page(paginator.num_pages)
        context['nbar'] = 'prods'
        context['tags'] = sorted(set([tag for item in context['items'] for tag in item.tags.names()]))
        return context


class TagServicesView(TagProductsView):
    """Catalogue view for the shop of all products and services."""

    model = Service

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(TagProductsView, self).get_context_data(**kwargs)
        context['nbar'] = 'servs'
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


class SingleServiceView(DetailView):
    """Detail view for a product."""

    template_name = 'service.html'
    model = Service

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(DetailView, self).get_context_data(**kwargs)
        context['nbar'] = 'servs'
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
