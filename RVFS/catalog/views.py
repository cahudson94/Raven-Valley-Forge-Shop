"""."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from account.models import Account, ShippingInfo, Order
from catalog.models import Product, Service, UserServiceImage as UserImage
from catalog.forms import ProductForm, ServiceForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from account.views import get_galleries, cart_count, unpack, split_cart
from datetime import datetime
from decimal import Decimal
import json


class AllItemsView(ListView):
    """List all items for inventory."""

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
            cart_item = {'item_id': self.get_object().id, 'type': 'prod',
                         'description': self.get_object().description}
            for field in fields:
                cart_item[field] = data[field]
                if field != 'quantity':
                    cart_item['description'] += ' ' + field + ', ' + data[field] + '. '
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
            item = json.dumps({'item_id': self.get_object().id, 'type': 'prod',
                               'description': self.get_object().description})
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
        if request.user.is_authenticated:
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
        if 'add' in data[0].keys():
            fields = []
            for field in data[0]:
                if field != 'csrfmiddlewaretoken' and field != 'add':
                    fields.append(field)
            cart_item = {'item_id': self.get_object().id, 'type': 'serv',
                         'description': self.get_object().description}
            for field in fields:
                cart_item[field] = data[0][field]
                if field in ['color', 'length', 'diameter', 'extras']:
                    cart_item['description'] += ' ' + field + ', ' + data[0][field] + '. '
            if data[1]:
                cart_item['files'] = ''
                for file in data[1]:
                    if data[1][file]:
                        image = UserImage(image=data[1][file])
                        image.save()
                        cart_item['files'] += file + ' ' + str(image.id) + ', '
            cart_item = json.dumps(cart_item)
            if self.request.user.is_anonymous:
                session = self.request.session
                if not session.get_expire_at_browser_close():
                    session.set_expiry(0)
                if 'account' not in self.request.session.keys():
                    session['account'] = {'cart': '', 'cart_total': 0.0}
                account = session['account']
                if account['cart']:
                    account['cart'] += '|' + cart_item
                else:
                    account['cart'] += cart_item
                if self.get_object().commission_fee:
                    account['cart_total'] = str(Decimal(self.get_object().commission_fee) +
                                                Decimal(account['cart_total']))
                session.save()
            else:
                account = Account.objects.get(user=request.user)
                if account.cart:
                    account.cart += '|' + cart_item
                else:
                    account.cart += cart_item
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
    success_url = reverse_lazy('checkout')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CartView, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            if not self.request.session.get_expire_at_browser_close():
                self.request.session.set_expiry(0)
            if 'account' not in self.request.session.keys():
                self.request.session['account'] = {'cart': '', 'cart_total': 0.0}
            context['cart'] = self.request.session['account']['cart']
            context['account'] = self.request.session['account']
            if 'shipping' in context['account'].keys():
                context['shipping'] = context['account']['shipping']
            if 'info' in context['account'].keys():
                context['info'] = context['account']['info']
        else:
            context['account'] = context['view'].request.user.account
            context['cart'] = context['account'].cart
            context['info'] = {'first': context['account'].first_name,
                               'last': context['account'].last_name,
                               'email': context['view'].request.user.email}
            context['shipping'] = ShippingInfo.objects.get(pk=context['account'].main_address)
            if len(context['account'].shippinginfo_set.values()) > 1:
                addresses = context['account'].shippinginfo_set.values()
                context['alt_add'] = [address for address in addresses]
        if context['cart']:
            context['cart'] = unpack(context['cart'])
            context['prods'] = []
            context['servs'] = []
            for item in context['cart']:
                if item['type'] == 'prod':
                    context['prods'].append(item)
                else:
                    context['servs'].append(item)
        context['item_fields'] = ['quantity', 'color', 'length', 'diameter', 'extras']
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'cart'
        return context

    def post(self, request, *args, **kwargs):
        """Apply shipping info for guest user."""
        data = request.POST
        field_count = 0
        fields = ['first_name', 'last_name', 'email',
                  'add_1', 'city', 'state', 'zip']
        if request.user.is_anonymous:
            request.session['account']['info'] = {'first': '', 'last': '', 'email': ''}
            if data['first_name']:
                request.session['account']['info']['first'] = data['first_name']
            if data['last_name']:
                request.session['account']['info']['last'] = data['last_name']
            if data['email']:
                request.session['account']['info']['email'] = data['email']
            request.session.save()
            request.session['account']['shipping'] = {'address1': '',
                                                      'address2': '',
                                                      'city': '',
                                                      'state': '',
                                                      'zip_code': ''}
            if data['add_1']:
                request.session['account']['shipping']['address1'] = data['add_1']
            if data['add_2']:
                request.session['account']['shipping']['address2'] = data['add_2']
            if data['city']:
                request.session['account']['shipping']['city'] = data['city']
            if data['state']:
                request.session['account']['shipping']['state'] = data['state']
            if data['zip']:
                request.session['account']['shipping']['zip_code'] = data['zip']
            request.session.save()
        for i in fields:
            if data[i]:
                field_count += 1
        if field_count == 7:
            shipping_data = {
                'info': {
                    'first': data['first_name'],
                    'last': data['last_name'],
                    'email': data['email'],
                },
                'shipping': {
                    'address1': data['add_1'],
                    'address2': data['add_2'],
                    'city': data['city'],
                    'state': data['state'],
                    'zip_code': data['zip'],
                }
            }
            if request.user.is_authenticated:
                account = Account.objects.get(user=request.user)
                exists = check_address(data, account)
                if exists:
                    shipping_data['exists'] = exists
            request.session['shipping_data'] = shipping_data
            request.session.save()
            return HttpResponseRedirect(self.success_url)
        return HttpResponseRedirect(reverse_lazy('cart'))


class CheckoutView(TemplateView):
    """Format order info to send to paypal."""

    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        """Check for shipping data."""
        if 'shipping_data' not in request.session.keys():
            return HttpResponseRedirect(reverse_lazy('cart'))
        return super(CheckoutView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CheckoutView, self).get_context_data(**kwargs)
        shipping_data = self.request.session['shipping_data']
        if context['view'].request.user.is_authenticated:
            account = context['view'].request.user.account
            cart = account.cart
            cart_total = account.cart_total
        else:
            guest_user = User.objects.get(username='Guest')
            account = Account.objects.get(user=guest_user)
            cart = self.request.session['account']['cart']
            cart_total = self.request.session['account']['cart_total']
        if 'exists' in shipping_data.keys():
            address = ShippingInfo.objects.get(id=shipping_data['exists'])
        else:
            address = ShippingInfo(
                address1=shipping_data['shipping']['address1'],
                address2=shipping_data['shipping']['address2'],
                zip_code=shipping_data['shipping']['zip_code'],
                city=shipping_data['shipping']['city'],
                state=shipping_data['shipping']['state'])
            address.save()
            if context['view'].request.user.is_authenticated:
                address.resident = Account.objects.get(user=context['view'].request.user)
            else:
                address.resident = Account.objects.get(user=guest_user)
            address.save()
        order = Order(
            buyer=account,
            order_content=cart,
            ship_to=address,
            recipient_email=shipping_data['info']['email'],
            recipient=(shipping_data['info']['first'] +
                       ', ' + shipping_data['info']['last'])
        )
        order.save()
        self.request.session['order_num'] = order.id
        self.request.session.save()
        context['shipping'] = address
        context['info'] = shipping_data['info']
        context['total'] = cart_total
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'cart'
        return context


class CheckoutCompleteView(TemplateView):
    """Checkout complete page which shifts products from cart to history and resets cart."""

    template_name = 'checkout_complete.html'

    def get(self, request, *args, **kwargs):
        """Check for shipping data."""
        if 'shipping_data' not in request.session.keys():
            return HttpResponseRedirect(reverse_lazy('cart'))
        return super(CheckoutCompleteView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CheckoutCompleteView, self).get_context_data(**kwargs)
        session = self.request.session
        context['order'] = session['order_num']
        if context['view'].request.user.is_authenticated:
            account = context['view'].request.user.account
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
        else:
            session['account'] = {'cart': '', 'cart_total': 0.0}
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'cart'
        return context


def check_address(data, account):
    """Check if user is using an existing address."""
    if 'address_name' in data.keys():
        add_id = data['address_name'].split(', ')[0].split(': ')[1]
        address = ShippingInfo.objects.get(id=add_id)
    else:
        address = ShippingInfo.objects.get(resident=account)
    equal = 0
    if data['add_1'] == address.address1:
        equal += 1
    if data['add_2'] == address.address2:
        equal += 1
    if data['city'] == address.city:
        equal += 1
    if data['state'] == address.state:
        equal += 1
    if data['zip'] == address.zip_code:
        equal += 1
    if equal == 5:
        return address.id
