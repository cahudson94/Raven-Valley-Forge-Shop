"""."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from account.models import Account, ShippingInfo, Order
from catalog.models import Product, Service
from catalog.forms import ProductForm, ServiceForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from account.views import get_galleries, cart_count, unpack, split_cart
from datetime import datetime
from decimal import Decimal
import json


class AllItemsView(ListView):

    template_name = 'list.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(AllItemsView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        context['cart_count'] = cart_count(self.request)
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
        context['cart_count'] = cart_count(self.request)
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
        context['cart_count'] = cart_count(self.request)
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
                                   .filter(tags__name__in=[self.kwargs.get('slug')]).all()
                                   .order_by('id'))
        paginator = Paginator(items, 20)
        page = context['view'].request.GET.get('page')
        try:
            context['items'] = paginator.page(page)
        except PageNotAnInteger:
            context['items'] = paginator.page(1)
        except EmptyPage:
            context['items'] = paginator.page(paginator.num_pages)
        context['cart_count'] = cart_count(self.request)
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
                                   .filter(tags__name__in=[self.kwargs.get('slug')]).all()
                                   .order_by('id'))
        paginator = Paginator(items, 20)
        page = context['view'].request.GET.get('page')
        try:
            context['items'] = paginator.page(page)
        except PageNotAnInteger:
            context['items'] = paginator.page(1)
        except EmptyPage:
            context['items'] = paginator.page(paginator.num_pages)
        context['cart_count'] = cart_count(self.request)
        context['nbar'] = 'servs'
        context['tags'] = sorted(set([tag for item in context['items'] for tag in item.tags.names()]))
        context['galleries'] = get_galleries()
        return context


class SingleProductView(DetailView):
    """Detail view for a product."""

    template_name = 'product.html'
    model = Product
    success_url = reverse_lazy('prods')

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
        context['cart_count'] = cart_count(self.request)
        context['nbar'] = 'prods'
        context['galleries'] = get_galleries()
        return context

    def post(self, request, *args, **kwargs):
        """Add item to appropriate list."""
        data = request.POST
        if 'add' in data.keys():
            fields = []
            for field in data:
                if field != 'csrfmiddlewaretoken' and field != 'add':
                    fields.append(field)
            cart_item = {'item_id': self.get_object().id, 'type': 'prod'}
            for field in fields:
                cart_item[field] = data[field]
            cart_item = json.dumps(cart_item)
            if self.request.user.is_anonymous:
                if not self.request.session.get_expire_at_browser_close():
                    self.request.session.set_expiry(0)
                if 'account' not in self.request.session.keys():
                    self.request.session['account'] = {'cart': '', 'cart_total': 0.0}
                account = self.request.session['account']
                if account['cart']:
                    account['cart'] += '|' + cart_item
                else:
                    account['cart'] += cart_item
                account['cart_total'] = str(Decimal(account['cart_total']) +
                                            Decimal(self.get_object().price))
                self.request.session.save()
            else:
                account = Account.objects.get(user=request.user)
                if account.cart:
                    account.cart += '|' + cart_item
                else:
                    account.cart += cart_item
                account.cart_total += Decimal(self.get_object().price)
                account.save()
        else:
            item = json.dumps({'item_id': self.get_object().id, 'type': 'prod'})
            if account.saved_products:
                account.saved_products += '|' + item
            else:
                account.saved_products += item
            account.save()
        return HttpResponseRedirect(self.success_url)


class SingleServiceView(DetailView):
    """Detail view for a service."""

    template_name = 'service.html'
    model = Service

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(SingleServiceView, self).get_context_data(**kwargs)
        if context['object'].extras:
            context['object'].extras = context['object'].extras.split(', ')
        context['cart_count'] = cart_count(self.request)
        context['nbar'] = 'servs'
        context['galleries'] = get_galleries()
        return context

    def post(self, request, *args, **kwargs):
        """Add item to appropriate list."""
        data = request.POST
        account = Account.objects.get(user=request.user)
        if 'add' in data.keys():
            success_url = reverse_lazy('serv_info', kwargs={'pk': self.get_object().id})
        else:
            success_url = reverse_lazy('servs')
            item = json.dumps({'item_id': self.get_object().id, 'type': 'serv'})
            if account.saved_services:
                account.saved_services += '|' + item
            else:
                account.saved_services += item
            account.save()
        return HttpResponseRedirect(success_url)


class ServiceInfoView(DetailView):
    """View for entering details to purchase a service."""

    template_name = 'service_info.html'
    model = Service
    success_url = reverse_lazy('servs')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ServiceInfoView, self).get_context_data(**kwargs)
        if context['object'].extras:
            context['object'].extras = context['object'].extras.split(', ')
        context['cart_count'] = cart_count(self.request)
        context['nbar'] = 'servs'
        context['galleries'] = get_galleries()
        return context

    def post(self, request, *args, **kwargs):
        """Add item to appropriate list."""
        data = request.POST, request.FILES
        if 'add' in data.keys():
            fields = []
            for field in data:
                if field != 'csrfmiddlewaretoken' and field != 'add':
                    fields.append(field)
            cart_item = {'item_id': self.get_object().id, 'type': 'serv'}
            for field in fields:
                cart_item[field] = data[field]
            cart_item = json.dumps(cart_item)
            if self.request.user.is_anonymous:
                if not self.request.session.get_expire_at_browser_close():
                    self.request.session.set_expiry(0)
                if 'account' not in self.request.session.keys():
                    self.request.session['account'] = {'cart': '', 'cart_total': Decimal(0.0)}
                account = self.request.session['account']
                if account['cart']:
                    account['cart'] += '|' + cart_item
                else:
                    account['cart'] += cart_item
                if self.get_object().commission_fee:
                    account['cart_total'] = str(Decimal(self.get_object().commission_fee) +
                                                Decimal(account['cart_total']))
                self.request.session.save()
            else:
                account = Account.objects.get(user=request.user)
                if account.cart:
                    account.cart += '|' + cart_item
                else:
                    account.cart += cart_item
                account.cart.append(cart_item)
                if self.get_object().commission_fee:
                    account.cart_total += Decimal(self.get_object().commission_fee)
                account.save()
        return HttpResponseRedirect(self.success_url)


class CreateProductView(PermissionRequiredMixin, CreateView):
    """View for creating a product."""

    permission_required = 'user.is_staff'
    template_name = 'create_product.html'
    model = Product
    success_url = reverse_lazy('prods')
    form_class = ProductForm

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CreateView, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
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
    success_url = reverse_lazy('prods')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(EditProductView, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
        context['nbar'] = 'prods'
        context['galleries'] = get_galleries()
        return context

    def form_valid(self, form):
        """Set date published if public."""
        if not form.instance.date_published:
            if form.instance.published == 'PB':
                form.instance.date_published = datetime.now()
        return super(EditProductView, self).form_valid(form)


class CreateServiceView(PermissionRequiredMixin, CreateView):
    """View for creating black smith services."""

    permission_required = 'user.is_staff'
    template_name = 'create_service.html'
    model = Service
    success_url = reverse_lazy('servs')
    form_class = ServiceForm

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CreateServiceView, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
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
    success_url = reverse_lazy('servs')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(EditServiceView, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
        context['nbar'] = 'servs'
        context['galleries'] = get_galleries()
        return context

    def form_valid(self, form):
        """Set date published if public."""
        if not form.instance.date_published:
            if form.instance.published == 'PB':
                form.instance.date_published = datetime.now()
        return super(EditServiceView, self).form_valid(form)


class CartView(TemplateView):
    """Cart and checkout page."""

    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CartView, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            if not self.request.session.get_expire_at_browser_close():
                self.request.session.set_expiry(0)
            if 'account' not in self.request.session.keys():
                self.request.session['account'] = {'cart': '', 'cart_total': Decimal(0.0)}
            context['cart'] = self.request.session['account']['cart']
            context['account'] = self.request.session['account']
        else:
            context['account'] = context['view'].request.user.account
            context['cart'] = context['account'].cart
        if context['cart']:
            cart_items = unpack(context['cart'])
            context['prods'] = []
            context['servs'] = []
            for item in cart_items:
                if item['type'] == 'prod':
                    context['prods'].append(item)
                else:
                    context['servs'].append(item)
        context['item_fields'] = ['quantity', 'color', 'length', 'diameter']
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'cart'
        return context


class CheckCompleteView(TemplateView):
    """Checkout complete page which shifts products from cart to history and resets cart."""

    template_name = 'checkout_complete.html'

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CheckCompleteView, self).get_context_data(**kwargs)
        account = context['view'].request.user.account
        order = Order(buyer=account, order_content=account.cart)
        order.save()
        context['order'] = order
        if account.cart:
            cart = split_cart(account.cart)
            if 'prods' in cart.keys():
                if account.purchase_history:
                    account.purchase_history += '|' + cart['prods']
                else:
                    account.purchase_history += cart['prods']
            if 'servs' in cart.keys():
                if account.service_history:
                    account.service_history += '|' + cart['servs']
                else:
                    account.service_history += cart['servs']
            account.cart = ''
            account.cart_total = 0.0
            account.save()
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'cart'
        return context
