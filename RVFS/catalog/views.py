"""."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from account.models import Account
from catalog.models import Product, Service
from catalog.forms import ProductForm, ServiceForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from account.views import get_galleries
from RVFS.google_calander import get_calendar
from datetime import datetime
from decimal import Decimal


class AllItemsView(ListView):

    template_name = 'list.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(AllItemsView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        context['nbar'] = 'list'
        context['galleries'] = get_galleries()
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
        context['galleries'] = get_galleries()
        return context


class AllServicesView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'catalog.html'
    model = Service

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
        context['nbar'] = 'servs'
        context['galleries'] = get_galleries()
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
        context['galleries'] = get_galleries()
        return context


class TagServicesView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'tagged_catalog.html'
    model = Service

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
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
        context['nbar'] = 'servs'
        context['tags'] = sorted(set([tag for item in context['items'] for tag in item.tags.names()]))
        context['galleries'] = get_galleries()
        return context


class SingleProductView(DetailView):
    """Detail view for a product."""

    template_name = 'product.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(SingleProductView, self).get_context_data(**kwargs)
        if context['object'].diameter:
            context['object'].diameter = context['object'].diameter.split(', ')
        if context['object'].length:
            context['object'].length = context['object'].length.split(', ')
        if context['object'].color:
            context['object'].color = context['object'].color.split(', ')
        if context['object'].extras:
            context['object'].extras = context['object'].extras.split(', ')
        context['nbar'] = 'prods'
        context['galleries'] = get_galleries()
        return context

    def post(self, request, *args, **kwargs):
        """Add item to appropriate list."""
        data = request.POST
        account = Account.objects.get(user=request.user)
        if 'add' in data.keys():
            success_url = reverse_lazy('prods')
            fields = []
            for field in data:
                if field != 'csrfmiddlewaretoken' and field != 'add':
                    fields.append(field)
            cart_item = {'item': self.get_object()}
            for field in fields:
                cart_item[field] = data[field]
            account.cart.append(cart_item)
            account.cart_total += Decimal(self.get_object().price)
            account.save()
        else:
            success_url = reverse_lazy('account')
            account.saved_products.append(self.get_object())
            account.save()
        return HttpResponseRedirect(success_url)


class SingleServiceView(DetailView):
    """Detail view for a product."""

    template_name = 'service.html'
    model = Service

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(SingleServiceView, self).get_context_data(**kwargs)
        if context['object'].extras:
            context['object'].extras = context['object'].extras.split(', ')
        context['nbar'] = 'servs'
        context['galleries'] = get_galleries()
        # context['calendar'] = get_calendar()
        # import pdb; pdb.set_trace()
        return context

    def post(self, request, *args, **kwargs):
        """Add item to appropriate list."""
        data = request.POST
        account = Account.objects.get(user=request.user)
        if 'add' in data.keys():
            success_url = reverse_lazy('prods')
            fields = []
            for field in data:
                if field != 'csrfmiddlewaretoken' and field != 'add':
                    fields.append(field)
            cart_item = {'item': self.get_object()}
            for field in fields:
                cart_item[field] = data[field]
            account.cart.append(cart_item)
            account.cart_total += Decimal(self.get_object().price)
            account.save()
        else:
            success_url = reverse_lazy('account')
            account.saved_products.append(self.get_object())
            account.save()
        return HttpResponseRedirect(success_url)


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
        context['galleries'] = get_galleries()
        return context

    def form_valid(self, form):
        """Set date published if public."""
        if form.instance.published == 'PB':
            form.instance.date_published = datetime.now()
        return super(CreateProductView, self).form_valid(form)


class EditProductView(PermissionRequiredMixin, UpdateView):
    """View for editing a product."""

    permission_required = 'user.is_staff'
    template_name = 'edit_product.html'
    model = Product
    form_class = ProductForm

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(EditProductView, self).get_context_data(**kwargs)
        context['nbar'] = 'prods'
        context['galleries'] = get_galleries()
        return context

    # def form_valid(self, form):
    #     """Update date published."""
    #     form.save()
    #     import pdb; pdb.set_trace()
    #     if form['published'].value() == 'PB':
    #         form['date_published'] = datetime.now()
    #     return


class CreateServiceView(PermissionRequiredMixin, CreateView):
    """View for creating black smith services."""

    permission_required = 'user.is_staff'
    template_name = 'create_service.html'
    model = Service
    success_url = reverse_lazy('home')
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CreateServiceView, self).get_context_data(**kwargs)
        context['nbar'] = 'add_serv'
        context['galleries'] = get_galleries()
        return context

    def form_valid(self, form):
        """Set date published if public."""
        if form.instance.published == 'PB':
            form.instance.date_published = datetime.now()
        return super(CreateServiceView, self).form_valid(form)


class EditServiceView(PermissionRequiredMixin, UpdateView):
    """View for editing a product."""

    permission_required = 'user.is_staff'
    template_name = 'edit_service.html'
    model = Service
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(EditServiceView, self).get_context_data(**kwargs)
        context['nbar'] = 'servs'
        context['galleries'] = get_galleries()
        return context


class CartView(TemplateView):
    """Cart and checkout page."""

    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CartView, self).get_context_data(**kwargs)
        context['nbar'] = 'cart'
        context['galleries'] = get_galleries()
        return context
