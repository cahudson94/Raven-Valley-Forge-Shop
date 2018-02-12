"""."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from account.views import get_galleries, cart_count, unpack, split_cart
from account.models import Account, ShippingInfo, Order
from catalog.models import Product, Service, UserServiceImage as UserImage
from catalog.forms import ProductForm, ServiceForm
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
                if field == 'extras':
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
        if 'shipping_data' in self.request.session.keys():
            context['shipping'] = self.request.session['shipping_data']['shipping']
            context['info'] = self.request.session['shipping_data']['info']
            if 'exists' in self.request.session['shipping_data'].keys():
                context['ship_exists'] = self.request.session['shipping_data']['exists']
        else:
            if self.request.user.is_authenticated:
                context['account'] = context['view'].request.user.account
                context['shipping'] = ShippingInfo.objects.get(pk=context['account'].main_address)
                context['info'] = {'first': context['account'].first_name,
                                   'last': context['account'].last_name,
                                   'email': context['view'].request.user.email}
        if 'service_data' in self.request.session.keys():
            context['serv_add'] = self.request.session['service_data']['shipping']
            context['serv_info'] = self.request.session['service_data']['info']
            if 'exists' in self.request.session['service_data'].keys():
                context['serv_exists'] = self.request.session['service_data']['exists']
        else:
            if self.request.user.is_authenticated:
                context['account'] = context['view'].request.user.account
                context['serv_add'] = ShippingInfo.objects.get(pk=context['account'].main_address)
                context['serv_info'] = {'first': context['account'].first_name,
                                        'last': context['account'].last_name,
                                        'email': context['view'].request.user.email}
        if self.request.user.is_anonymous:
            if not self.request.session.get_expire_at_browser_close():
                self.request.session.set_expiry(0)
            if 'account' not in self.request.session.keys():
                self.request.session['account'] = {'cart': '', 'cart_total': 0.0}
            context['cart'] = self.request.session['account']['cart']
            context['account'] = self.request.session['account']
        else:
            context['account'] = context['view'].request.user.account
            context['cart'] = context['account'].cart
            if len(context['account'].shippinginfo_set.values()) > 1:
                addresses = context['account'].shippinginfo_set.values()
                context['alt_add'] = [address for address in addresses]
        if context['cart']:
            context['cart'] = unpack(context['cart'])
            context['prods'] = []
            context['servs'] = []
            context['serv_address'] = False
            for item in context['cart']:
                if item['type'] == 'prod':
                    item['count'] = 'prod ' + str(len(context['prods']))
                    context['prods'].append(item)
                else:
                    if item['item'].requires_address:
                        context['serv_address'] = True
                    item['count'] = 'serv ' + str(len(context['servs']))
                    context['servs'].append(item)
        context['item_fields'] = ['color', 'length', 'diameter', 'extras']
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'cart'
        return context

    def post(self, request, *args, **kwargs):
        """Apply shipping info for guest user."""
        data = request.POST
        exists = False
        exists_serv = False
        field_count = 0
        ship_fields = ['ship_first_name', 'ship_last_name', 'ship_email',
                       'ship_add_1', 'ship_city', 'ship_state', 'ship_zip']
        serv_fields = ['serv_first_name', 'serv_last_name', 'serv_email',
                       'serv_add_1', 'serv_city', 'serv_state', 'serv_zip']
        if 'ship_first_name' in data.keys():
            if request.user.is_authenticated:
                account = Account.objects.get(user=request.user)
                exists = check_address(data, account, 0)
            for i in ship_fields:
                if data[i]:
                    field_count += 1
            if field_count == 7:
                shipping_data = {
                    'info': {
                        'first': data['ship_first_name'],
                        'last': data['ship_last_name'],
                        'email': data['ship_email'],
                    },
                    'shipping': {
                        'address1': data['ship_add_1'],
                        'address2': data['ship_add_2'],
                        'city': data['ship_city'],
                        'state': data['ship_state'],
                        'zip_code': data['ship_zip'],
                    }
                }
                request.session['shipping_data'] = shipping_data
                request.session.save()
        if 'serv_first_name' in data.keys():
            if request.user.is_authenticated:
                account = Account.objects.get(user=request.user)
                exists_serv = check_address(data, account, 1)
            field_count = 0
            for i in serv_fields:
                if data[i]:
                    field_count += 1
            if field_count == 7:
                serv_data = {
                    'info': {
                        'first': data['serv_first_name'],
                        'last': data['serv_last_name'],
                        'email': data['serv_email'],
                    },
                    'shipping': {
                        'address1': data['serv_add_1'],
                        'address2': data['serv_add_2'],
                        'city': data['serv_city'],
                        'state': data['serv_state'],
                        'zip_code': data['serv_zip'],
                    }
                }
                request.session['service_data'] = serv_data
                request.session.save()
        if exists:
            shipping_data['exists'] = exists
        if exists_serv:
            serv_data['exists'] = exists_serv
        if field_count == 7:
            return HttpResponseRedirect(self.success_url)
        return HttpResponseRedirect(reverse_lazy('cart'))


@login_required
def update_cart(request):
    """Change quantity of items in cart and update total."""
    cart_item = request.GET['cart_data'].split(' ')
    if request.user.is_authenticated:
        cart = unpack(request.user.account.cart)
        cart_total = request.user.account.cart_total
    else:
        cart = unpack(request.session['account']['cart'])
        cart_total = request.session['account']['cart_total']
    prods = []
    servs = []
    for item in cart:
        if item['type'] == 'prod':
            prods.append(item)
        else:
            servs.append(item)
    if cart_item[0] == 'prod':
        difference = int(request.GET['quantity']) - int(prods[int(cart_item[1])]['quantity'])
        cart_total += Decimal(prods[int(cart_item[1])]['item'].price * difference)
        prods[int(cart_item[1])]['quantity'] = request.GET['quantity']
    cart_repack(prods, servs, request, cart_total)
    return HttpResponse(cart_total)


@login_required
def delete_item(request):
    """Remove items from cart and update total."""
    cart_item = request.GET['item'].split(' ')
    if request.user.is_authenticated:
        cart = unpack(request.user.account.cart)
        cart_total = request.user.account.cart_total
    else:
        cart = unpack(request.session['account']['cart'])
        cart_total = request.session['account']['cart_total']
    prods = []
    servs = []
    for item in cart:
        if item['type'] == 'prod':
            prods.append(item)
        else:
            servs.append(item)
    if len(prods) + len(servs) == 1:
        cart_total = Decimal(0.0)
        if request.user.is_authenticated:
            request.user.account.cart_total = cart_total
            request.user.account.cart = ''
            request.user.account.save()
        else:
            request.session['account']['cart_total'] = cart_total
            request.session['account']['cart'] = ''
            request.session.save()
        return HttpResponse('empty')
    if cart_item[0] == 'prod':
        cart_total -= Decimal(prods[int(cart_item[1])]['item'].price * int(prods[int(cart_item[1])]['quantity']))
        prods.pop(int(cart_item[1]))
    else:
        if servs[int(cart_item[1])]['item'].commission_fee:
            cart_total -= Decimal(servs[int(cart_item[1])]['item'].commission_fee)
        servs.pop(int(cart_item[1]))
    cart_repack(prods, servs, request, cart_total)
    return HttpResponse(cart_total)


class CheckoutView(TemplateView):
    """Format order info to send to paypal."""

    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        """Check for shipping data."""
        if 'shipping_data' not in request.session.keys() and 'service_data' not in request.session.keys():
            return HttpResponseRedirect(reverse_lazy('cart'))
        return super(CheckoutView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        shipping_data = ''
        service_data = ''
        serv_address = ''
        address = ''
        context = super(CheckoutView, self).get_context_data(**kwargs)
        if 'shipping_data' in self.request.session.keys():
            shipping_data = self.request.session['shipping_data']
        if 'service_data' in self.request.session.keys():
            service_data = self.request.session['service_data']
        if context['view'].request.user.is_authenticated:
            account = context['view'].request.user.account
            cart = account.cart
            cart_total = account.cart_total
        else:
            guest_user = User.objects.get(username='Guest')
            account = Account.objects.get(user=guest_user)
            cart = self.request.session['account']['cart']
            cart_total = self.request.session['account']['cart_total']
        if shipping_data:
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
            email = shipping_data['info']['email']
            name = (shipping_data['info']['first'] +
                    ', ' + shipping_data['info']['last'])
        if service_data:
            if 'exists' in service_data.keys():
                if address:
                    serv_address = ShippingInfo.objects.get(id=service_data['exists'])
                else:
                    address = ShippingInfo.objects.get(id=service_data['exists'])
            else:
                if address:
                    serv_address = ShippingInfo(
                        address1=service_data['shipping']['address1'],
                        address2=service_data['shipping']['address2'],
                        zip_code=service_data['shipping']['zip_code'],
                        city=service_data['shipping']['city'],
                        state=service_data['shipping']['state'])
                    serv_address.save()
                    if context['view'].request.user.is_authenticated:
                        serv_address.resident = Account.objects.get(user=context['view'].request.user)
                    else:
                        serv_address.resident = Account.objects.get(user=guest_user)
                    serv_address.save()
                else:
                    address = ShippingInfo(
                        address1=service_data['shipping']['address1'],
                        address2=service_data['shipping']['address2'],
                        zip_code=service_data['shipping']['zip_code'],
                        city=service_data['shipping']['city'],
                        state=service_data['shipping']['state'])
                    address.save()
                    if context['view'].request.user.is_authenticated:
                        address.resident = Account.objects.get(user=context['view'].request.user)
                    else:
                        address.resident = Account.objects.get(user=guest_user)
                    address.save()
        if serv_address and address:
            order = Order(
                buyer=account,
                order_content=cart,
                ship_to=address,
                recipient_email=email,
                recipient=name,
                serv_address=serv_address,
            )
            order.save()
        elif shipping_data:
            order = Order(
                buyer=account,
                order_content=cart,
                ship_to=address,
                recipient_email=email,
                recipient=name,
            )
            order.save()
        else:
            order = Order(
                buyer=account,
                order_content=cart,
                serv_address=address,
                recipient_email=email,
                recipient=name,
            )
            order.save()
        self.request.session['order_num'] = order.id
        self.request.session.save()
        if shipping_data:
            context['shipping'] = address
            context['info'] = shipping_data['info']
            if service_data:
                context['serv'] = serv_address
        elif service_data:
            context['serv'] = address
            context['info'] = service_data['info']
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
        if 'shipping_data' not in request.session.keys() or 'service_data' not in request.session.keys():
            return HttpResponseRedirect(reverse_lazy('cart'))
        return super(CheckoutCompleteView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CheckoutCompleteView, self).get_context_data(**kwargs)
        session = self.request.session
        context['order'] = session['order_num']
        order = Order.objects.get(session['order_num'])
        order.paid = True
        order.save()
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


def check_address(data, account, version):
    """Check if user is using an existing address."""
    types = ['ship_address_name', 'serv_address_name']
    types_data = {
        'ship_address_name': ['ship_add_1', 'ship_add_2',
                              'ship_city', 'ship_state', 'ship_zip'],
        'serv_address_name': ['serv_add_1', 'serv_add_2',
                              'serv_city', 'serv_state', 'serv_zip']
    }
    if types[version] in data.keys():
        add_id = data[types[version]].split(', ')[0].split(': ')[1]
        address = ShippingInfo.objects.get(id=add_id)
    else:
        address = ShippingInfo.objects.get(resident=account)
    types_data['address'] = [address.address1, address.address2,
                             address.city, address.state, address.zip_code]
    equal = 0
    for idx, item in enumerate(types_data[types[version]]):
        if data[item] == types_data['address'][idx]:
            equal += 1
    if equal == 5:
        return address.id


def cart_repack(prods, servs, request, cart_total):
    """Repack items into the cart."""
    cart_repack = ''
    for i in prods:
        i.pop('item')
        if cart_repack:
            cart_repack += '|' + json.dumps(i)
        else:
            cart_repack += json.dumps(i)
    for i in servs:
        i.pop('item')
        if cart_repack:
            cart_repack += '|' + json.dumps(i)
        else:
            cart_repack += json.dumps(i)
    if request.user.is_authenticated:
        request.user.account.cart = cart_repack
        request.user.account.cart_total = cart_total
        request.user.account.save()
    else:
        request.session['account']['cart'] = cart_repack
        request.session['account']['cart_total'] = cart_total
        request.session.save()