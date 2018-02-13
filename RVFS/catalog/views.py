"""Various views for the catalog and cart."""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from account.models import Account, ShippingInfo, Order
from account.views import unpack, split_cart, set_basic_context
from catalog.forms import ProductForm, ServiceForm
from catalog.models import Product, Service, UserServiceImage as UserImage
from datetime import datetime
from decimal import Decimal
from RVFS.google_calendar import check_time_slot, set_appointment
import json
import os


MONTHS = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'
}


class AllItemsView(ListView):
    """List all items for inventory."""

    template_name = 'list.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(AllItemsView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        set_basic_context(context, 'list')
        return context


class AllProductsView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'catalog.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        items = self.model.objects.filter(published='PB')
        context['all_tags'] = sorted(set([tag for item in
                                          items for tag in
                                          item.tags.names()]))
        paginator = Paginator(context['all_tags'], 5)
        request = self.request
        if 'page' in request.GET:
            page = self.request.GET.get('page')
        else:
            page = 1
        try:
            context['tags'] = paginator.page(page)
        except PageNotAnInteger:
            context['tags'] = paginator.page(1)
        except EmptyPage:
            context['tags'] = paginator.page(paginator.num_pages)
        context['items'] = {tag: [item for item in
                                  items if tag in
                                  item.tags.names()] for tag in
                            context['tags']}
        set_basic_context(context, 'prods')
        return context


class AllServicesView(ListView):
    """Catalogue view for the shop of all products and services."""

    template_name = 'catalog.html'
    model = Service

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        items = self.model.objects.filter(published='PB')
        context['all_tags'] = sorted(set([tag for item in
                                          items for tag in
                                          item.tags.names()]))
        paginator = Paginator(context['all_tags'], 5)
        request = self.request
        if 'page' in request.GET:
            page = self.request.GET.get('page')
        else:
            page = 1
        try:
            context['tags'] = paginator.page(page)
        except PageNotAnInteger:
            context['tags'] = paginator.page(1)
        except EmptyPage:
            context['tags'] = paginator.page(paginator.num_pages)
        context['items'] = {tag: [item for item in
                                  items if tag in
                                  item.tags.names()] for tag in
                            context['tags']}
        set_basic_context(context, 'servs')
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
        context['all_tags'] = sorted(set([tag for item in
                                          all_items for tag in
                                          item.tags.names()]))
        slugs = self.kwargs.get('slug')
        items = (self.model.objects.filter(published='PB')
                                   .filter(tags__name__in=[slugs]).all()
                                   .order_by('id'))
        paginator = Paginator(items, 20)
        page = self.request.GET.get('page')
        try:
            context['items'] = paginator.page(page)
        except PageNotAnInteger:
            context['items'] = paginator.page(1)
        except EmptyPage:
            context['items'] = paginator.page(paginator.num_pages)
        context['tags'] = sorted(set([tag for item in
                                      context['items'] for tag in
                                      item.tags.names()]))
        set_basic_context(context, 'prods')
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
        context['all_tags'] = sorted(set([tag for item in
                                          all_items for tag in
                                          item.tags.names()]))
        slugs = self.kwargs.get('slug')
        items = (self.model.objects.filter(published='PB')
                                   .filter(tags__name__in=[slugs]).all()
                                   .order_by('id'))
        paginator = Paginator(items, 20)
        page = self.request.GET.get('page')
        try:
            context['items'] = paginator.page(page)
        except PageNotAnInteger:
            context['items'] = paginator.page(1)
        except EmptyPage:
            context['items'] = paginator.page(paginator.num_pages)
        context['tags'] = sorted(set([tag for item in
                                      context['items'] for tag in
                                      item.tags.names()]))
        set_basic_context(context, 'servs')
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
        set_basic_context(context, 'prods')
        return context

    def post(self, request, *args, **kwargs):
        """Add item to appropriate list."""
        data = request.POST
        extra_cost = ''
        if 'add' in data.keys():
            fields = []
            for field in data:
                if field != 'csrfmiddlewaretoken' and field != 'add':
                    fields.append(field)
            cart_item = {'item_id': self.get_object().id, 'type': 'prod',
                         'description': self.get_object().description}
            for field in fields:
                if data[field]:
                    cart_item[field] = data[field]
                if data[field] != '----' and field == 'extras':
                    extra_cost = Decimal(data[field].split(': ')[1][1:])
            cart_item = json.dumps(cart_item)
            price = Decimal(self.get_object().price)
            if extra_cost:
                price += extra_cost
            if self.request.user.is_anonymous:
                if not self.request.session.get_expire_at_browser_close():
                    self.request.session.set_expiry(0)
                if 'account' not in self.request.session.keys():
                    self.request.session['account'] = {'cart': '',
                                                       'cart_total': 0.0}
                account = self.request.session['account']
                if account['cart']:
                    account['cart'] += '|' + cart_item
                else:
                    account['cart'] += cart_item
                account['cart_total'] = str(Decimal(account['cart_total']) +
                                            Decimal(price))
                self.request.session.save()
            else:
                account = Account.objects.get(user=request.user)
                if account.cart:
                    account.cart += '|' + cart_item
                else:
                    account.cart += cart_item
                account.cart_total += Decimal(price)
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
        set_basic_context(context, 'servs')
        return context

    def post(self, request, *args, **kwargs):
        """Add item to appropriate list."""
        data = request.POST
        if request.user.is_authenticated:
            account = Account.objects.get(user=request.user)
        if 'add' in data.keys():
            success_url = reverse_lazy('serv_info',
                                       kwargs={'pk': self.get_object().id})
        else:
            success_url = reverse_lazy('servs')
            item = json.dumps({'item_id': self.get_object().id,
                               'type': 'serv'})
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
        set_basic_context(context, 'servs')
        return context

    def post(self, request, *args, **kwargs):
        """Add item to appropriate list."""
        data = request.POST, request.FILES
        extra_cost = ''
        price = ''
        if 'add' in data[0].keys():
            fields = []
            for field in data[0]:
                if field != 'csrfmiddlewaretoken' and field != 'add':
                    fields.append(field)
            cart_item = {'item_id': self.get_object().id, 'type': 'serv',
                         'description': self.get_object().description}
            for field in fields:
                if data[0][field]:
                    cart_item[field] = data[0][field]
                if data[0][field] != '----' and field == 'extras':
                    extra_cost = Decimal(data[0][field].split(': ')[1][1:])
            if data[1]:
                cart_item['files'] = ''
                for file in data[1]:
                    if data[1][file]:
                        image = UserImage(image=data[1][file])
                        image.save()
                        if cart_item['files']:
                            cart_item['files'] += ', ' + file
                            cart_item['files'] += ' ' + str(image.id)
                        else:
                            cart_item['files'] += file + ' ' + str(image.id)
            cart_item = json.dumps(cart_item)
            if self.get_object().commission_fee:
                price = self.get_object().commission_fee
                if extra_cost:
                    price += extra_cost
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
                if price:
                    account['cart_total'] = str(Decimal(price) +
                                                Decimal(account['cart_total']))
                session.save()
            else:
                account = Account.objects.get(user=request.user)
                if account.cart:
                    account.cart += '|' + cart_item
                else:
                    account.cart += cart_item
                if price:
                    account.cart_total += Decimal(price)
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
        set_basic_context(context, 'add_prod')
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
        set_basic_context(context, 'prods')
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
        set_basic_context(context, 'add_serv')
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
        set_basic_context(context, 'servs')
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
        session = self.request.session
        info = ShippingInfo.objects
        if self.request.user.is_authenticated:
            account = self.request.user.account
            context['account'] = account
        if 'shipping_data' in self.request.session.keys():
            context['shipping'] = session['shipping_data']['shipping']
            context['info'] = session['shipping_data']['info']
            if 'exists' in session['shipping_data'].keys():
                context['ship_exists'] = session['shipping_data']['exists']
        elif self.request.user.is_authenticated:
            context['shipping'] = info.get(pk=account.main_address)
            context['info'] = {'first': account.first_name,
                               'last': account.last_name,
                               'email': self.request.user.email}
        if 'service_data' in session.keys():
            context['serv_add'] = session['service_data']['shipping']
            context['serv_info'] = session['service_data']['info']
            if 'exists' in session['service_data'].keys():
                context['serv_exists'] = session['service_data']['exists']
        elif self.request.user.is_authenticated:
            context['serv_add'] = info.get(pk=account.main_address)
            context['serv_info'] = {'first': account.first_name,
                                    'last': account.last_name,
                                    'email': self.request.user.email}
        if self.request.user.is_anonymous:
            if not session.get_expire_at_browser_close():
                session.set_expiry(0)
            if 'account' not in session.keys():
                session['account'] = {'cart': '', 'cart_total': 0.0}
            cart = session['account']['cart']
            context['account'] = session['account']
        else:
            cart = context['account'].cart
            if len(context['account'].shippinginfo_set.values()) > 1:
                addresses = context['account'].shippinginfo_set.values()
                context['alt_add'] = [address for address in addresses]
        if cart:
            context['cart'] = unpack(cart)
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
        set_basic_context(context, 'cart')
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
        difference = (int(request.GET['quantity']) -
                      int(prods[int(cart_item[1])]['quantity']))
        cart_total += Decimal(prods[int(cart_item[1])]['item'].price *
                              difference)
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
        cart_total -= Decimal(prods[int(cart_item[1])]['item'].price *
                              int(prods[int(cart_item[1])]['quantity']))
        prods.pop(int(cart_item[1]))
    else:
        fee = servs[int(cart_item[1])]['item'].commission_fee
        if fee:
            cart_total -= Decimal(fee)
        servs.pop(int(cart_item[1]))
    cart_repack(prods, servs, request, cart_total)
    return HttpResponse(cart_total)


class CheckoutView(TemplateView):
    """Format order info to send to paypal."""

    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        """Check for shipping data."""
        keys = request.session.keys()
        if 'shipping_data' not in keys and 'service_data' not in keys:
            return HttpResponseRedirect(reverse_lazy('cart'))
        return super(CheckoutView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        shipping_data = ''
        service_data = ''
        serv_address = ''
        address = ''
        acc_obj = Account.objects
        context = super(CheckoutView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user = self.request.user
            account = self.request.user.account
            cart = account.cart
            cart_total = account.cart_total
        else:
            user = User.objects.get(username='Guest')
            account = Account.objects.get(user=user)
            cart = self.request.session['account']['cart']
            cart_total = self.request.session['account']['cart_total']
        if 'shipping_data' in self.request.session.keys():
            shipping_data = self.request.session['shipping_data']
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
                address.resident = acc_obj.get(user=user)
                address.save()
            email = shipping_data['info']['email']
            name = (shipping_data['info']['first'] +
                    ', ' + shipping_data['info']['last'])
        if 'service_data' in self.request.session.keys():
            service_data = self.request.session['service_data']
            if 'exists' in service_data.keys():
                ship_obj = ShippingInfo.objects
                if address:
                    serv_address = ship_obj.get(id=service_data['exists'])
                else:
                    address = ship_obj.get(id=service_data['exists'])
            else:
                if address:
                    serv_address = ShippingInfo(
                        address1=service_data['shipping']['address1'],
                        address2=service_data['shipping']['address2'],
                        zip_code=service_data['shipping']['zip_code'],
                        city=service_data['shipping']['city'],
                        state=service_data['shipping']['state'])
                    serv_address.save()
                    serv_address.resident = acc_obj.get(user=user)
                    serv_address.save()
                else:
                    address = ShippingInfo(
                        address1=service_data['shipping']['address1'],
                        address2=service_data['shipping']['address2'],
                        zip_code=service_data['shipping']['zip_code'],
                        city=service_data['shipping']['city'],
                        state=service_data['shipping']['state'])
                    address.save()
                    address.resident = Account.objects.get(user=user)
                    address.save()
        order = Order(
            buyer=account,
            order_content=cart,
            recipient_email=email,
            recipient=name,
        )
        order.save()
        if serv_address and address:
            order.ship_to = address
            order.serv_address = serv_address
            order.save()
        elif shipping_data:
            order.ship_to = address
            order.save()
        else:
            order.serv_address = address
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
        set_basic_context(context, 'cart')
        return context


class CheckoutCompleteView(TemplateView):
    """Checkout complete page, shifts cart to history and resets."""

    template_name = 'checkout_complete.html'

    def get(self, request, *args, **kwargs):
        """Check for shipping data."""
        keys = request.session.keys()
        view = CheckoutCompleteView
        if 'shipping_data' not in keys or 'service_data' not in keys:
            return HttpResponseRedirect(reverse_lazy('cart'))
        return super(view, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CheckoutCompleteView, self).get_context_data(**kwargs)
        session = self.request.session
        context['order'] = session['order_num']
        order = Order.objects.get(id=session['order_num'])
        order.paid = True
        order.save()
        files = False
        reschedule = []
        serv_names = []
        serv_times = []
        schedualed = []
        not_schedualed = []
        if self.request.user.is_authenticated:
            account = self.request.user.account
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
        else:
            cart = split_cart(session['account']['cart'])
        if 'servs' in cart.keys():
            servs = unpack(cart['servs'])
            for serv in servs:
                serv_names.append(serv['item'].name)
                if 'files' in serv.keys():
                    files = True
                    for file in serv['files'].split(', '):
                        image = UserImage.objects.get(id=file.split(' ')[1])
                        image.used = True
                        image.save()
                if 'day' in serv.keys():
                    reschedule.append(attempt_appointment(serv, session))
                    time = (serv['month'] + ' ' +
                            serv['day'] + ', ' +
                            serv['year'] + ' at ' + serv['hour'])
                    serv_times.append(time)
                else:
                    serv_times.append(None)
        for idx, i in enumerate(reschedule):
            if i:
                not_schedualed.append([serv_names[idx], serv_times[idx]])
            else:
                schedualed.append([serv_names[idx], serv_times[idx]])
        email = 'ravenmoorevalleyforge@gmail.com'
        subject = 'Order #{} Confirmation'.format(context['order'])
        if 'shipping_data' in session.keys():
            info = session['shipping_data']['info']
        else:
            info = session['service_data']['info']
        name = info['first'] + ', ' + info['last']
        if True in reschedule:
            owner_body = '{} tried to schedual '.format(name)
            owner_body += serv_names[0]
            if len(serv_names) > 1:
                for i in serv_names[1:-1]:
                    owner_body += ', ' + i
                owner_body += ', and ' + serv_names[-1]
            owner_body += ' service(s) for '
            owner_body += serv_times[0]
            if len(serv_times) > 1:
                for i in serv_times[1:-1]:
                    owner_body += ', ' + i
                owner_body += ', and ' + serv_times[-1]
            owner_body += ' time(s). \nYou have one or more \
schedual conflicts with '
            owner_body += not_schedualed[0][0]
            if len(not_schedualed) > 1:
                for i in not_schedualed[1:-1]:
                    owner_body += ', ' + i[0]
                owner_body += ', and ' + not_schedualed[-1][0]
            owner_body += ' service(s) at '
            owner_body += not_schedualed[0][1]
            if len(not_schedualed) > 1:
                for i in not_schedualed[1:-1]:
                    owner_body += ', ' + i[1]
                owner_body += ', and ' + not_schedualed[-1][1]
            owner_body += ' times(s), please contact \
them at {} to set a new time.'.format(info['email'])
            if 'prods' in cart.keys():
                client_body = 'All ordered products are confirmed, however one or \
more of the times you tried to book are not available. You will be contacted \
to reschedule these appointments:\n\n'
            else:
                client_body = 'One or more of the times you tried to book \
are not available. You will be contacted to reschedule these appointments:\n\n'
            for i in not_schedualed:
                client_body += i[0] + ' at ' + i[1] + '\n'
        else:
            if schedualed:
                owner_body = '{} is schedualed for:'.format(name)
                owner_body += schedualed[0][0] + ' at ' + schedualed[0][1]
                for i in schedualed:
                    owner_body += i[0] + ' at ' + i[1] + '\n'
                if 'prods' in cart.keys():
                    client_body = 'All of your products and services are confirmed.\n'
                else:
                    client_body = 'All of your services are confirmed.\n'
        if schedualed:
            client_body += 'These services were schedualed successfully:\n'
            for i in schedualed:
                client_body += i[0] + ' at ' + i[1] + '\n'
        if 'prods' in cart.keys():
            owner_body += ' They purchased:\n'
            client_body += '\nYou will recieve an email with tracking info \
when your order ships. Your purchases:\n\n'
            prods = unpack(cart['prods'])
            for prod in prods:
                owner_body += prod['quantity'] + 'x ' + prod['item'].name
                client_body += prod['quantity'] + 'x ' + prod['item'].name
                if 'color' in prod.keys():
                    owner_body += ' color: ' + prod['color']
                    client_body += ' color: ' + prod['color']
                if 'length' in prod.keys():
                    owner_body += ' length: ' + prod['length']
                    client_body += ' length: ' + prod['length']
                if 'diameter' in prod.keys():
                    owner_body += ' diameter: ' + prod['diameter']
                    client_body += ' diameter: ' + prod['diameter']
                if 'extras' in prod.keys():
                    owner_body += ' extras: ' + prod['extras'].split(': ')[0]
                    client_body += ' extras: ' + prod['extras'].split(': ')[0]
                owner_body += '\n'
                client_body += '\n'
        owner_email = EmailMessage(subject,
                                   owner_body,
                                   'rvfmsite@gmail.com',
                                   [email])
        client_email = EmailMessage(subject,
                                    client_body,
                                    email,
                                    [info['email']])
        if files:
            for serv in servs:
                for file in serv['files'].split(', '):
                    image = UserImage.objects.get(id=file.split(' ')[1])
                    img_path = os.path.join(settings.BASE_DIR, 'media',
                                            image.image.name)
                    owner_email.attach_file(img_path)
        owner_email.send(fail_silently=True)
        client_email.send(fail_silently=True)
        if self.request.user.is_authenticated:
            account.cart = ''
            account.cart_total = 0.0
            account.save()
        else:
            session['account'] = {'cart': '', 'cart_total': 0.0}
        set_basic_context(context, 'cart')
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


def attempt_appointment(servs, session):
    """Set appointment or return reschedule."""
    day = servs['day']
    month = MONTHS[servs['month']]
    year = servs['year']
    if servs['hour'].split(' ')[1] == 'AM':
        hour = servs['hour'].split(' ')[0]
    else:
        hour = servs['hour'].split(' ')[0]
        hour = str(int(hour) + 12)
    time = [year, month, day, int(hour)]
    busy = check_time_slot(time)
    if busy:
        return True
    else:
        info = session['service_data']['info']
        set_appointment(time, info)
        return False
