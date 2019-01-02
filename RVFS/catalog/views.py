"""Various views for the catalog and cart."""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from account.models import Account, ShippingInfo, Order
from account.views import (
    unpack, split_cart, set_basic_context,
    valid_staff, get_state
)
from catalog.forms import ProductForm, ServiceForm, QuoteForm
from catalog.models import Product, Service, Discount
from datetime import datetime
from decimal import Decimal
import easypost
import json
import os
import paypalrestsdk
import taxjar


easypost.api_key = os.environ.get('EASYPOST_API_KEY')
taxjar_client = taxjar.Client(api_key=os.environ.get('TAXJAR_API_KEY'))

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


class AllItemsView(UserPassesTestMixin, ListView):
    """List all items for inventory."""

    template_name = 'list.html'
    model = Product

    def test_func(self):
        """Validate access."""
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(AllItemsView, self).get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        set_basic_context(context, 'list')
        return context


class CatalogueView(ListView):
    """Catalogue view for the shop of all products."""

    template_name = 'catalog.html'
    model = Product

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        all_items = self.model.objects.filter(published='PB')
        context['all_tags'] = sorted(set([tag for item in
                                          all_items for tag in
                                          item.catagories.names()]))
        if slug:
            context['slug'] = slug
            items = (self.model.objects.filter(published='PB')
                                       .filter(catagories__name__in=[slug])
                                       .all()
                                       .order_by('id'))
            page_content = items
        else:
            items = all_items
            page_content = context['all_tags']
        paginator = Paginator(page_content, 5)
        if 'page' in self.request.GET:
            page = self.request.GET.get('page')
        else:
            page = 1
        try:
            context['page'] = paginator.page(page)
        except PageNotAnInteger:
            context['page'] = paginator.page(1)
        except EmptyPage:
            context['page'] = paginator.page(paginator.num_pages)
        if slug:
            context['items'] = set([item for item in items])
        else:
            context['items'] = {tag: [item for item in
                                all_items if tag in
                                item.catagories.names()] for tag in
                                context['page']}
        set_basic_context(context, 'prods')
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
        if self.request.user.is_authenticated:
            account = Account.objects.get(user=request.user)
        buy_type = ''
        if 'add' in data.keys():
            buy_type = 'add'
        elif 'pre_order' in data.keys():
            buy_type = 'pre_order'
        if buy_type:
            fields = []
            for field in data:
                if field not in ['add', 'pre_order', 'csrfmiddlewaretoken']:
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
            item_total = (Decimal(price) * Decimal(data['quantity']))
            if self.request.user.is_anonymous:
                if not self.request.session.get_expire_at_browser_close():
                    self.request.session.set_expiry(0)
                if 'account' not in self.request.session.keys():
                    self.request.session['account'] = {'cart': '',
                                                       'cart_total': 0.0,
                                                       'pre_order': '',
                                                       'pre_order_total': 0.0}
                account = self.request.session['account']
                if buy_type == 'pre_order':
                    if account['pre_order']:
                        account['pre_order'] += '|' + cart_item
                    else:
                        account['pre_order'] += cart_item
                    account['pre_order_total'] = str(
                        Decimal(account['pre_order_total']) + item_total)
                else:
                    if account['cart']:
                        account['cart'] += '|' + cart_item
                    else:
                        account['cart'] += cart_item
                    account['cart_total'] = str(
                        Decimal(account['cart_total']) + item_total)
                self.request.session.save()
            else:
                if buy_type == 'pre_order':
                    if account.pre_order:
                        account.pre_order += '|' + cart_item
                    else:
                        account.pre_order += cart_item
                    account.pre_order_total += Decimal(item_total)
                else:
                    if account.cart:
                        account.cart += '|' + cart_item
                    else:
                        account.cart += cart_item
                    account.cart_total += Decimal(item_total)
                account.save()
        else:
            item = str(self.get_object().id)
            if account.saved_products:
                if item not in account.saved_products.split(', '):
                    account.saved_products += ', ' + item
            else:
                account.saved_products += item
            account.save()
        return HttpResponseRedirect(self.success_url)


class DeleteProductView(DeleteView, UserPassesTestMixin):
    """Remove an existing product."""

    model = Product
    success_url = reverse_lazy('prods')
    template_name = 'delete_product.html'

    def test_func(self):
        """Validate access."""
        return self.request.user.is_staff


@login_required
@user_passes_test(valid_staff)
def copy_prod(request, pk):
    """Copy a product."""
    prod = Product.objects.get(pk=pk)
    new_pk = Product.objects.last().pk + 1
    prod.pk = new_pk
    prod.name += ' Copy'
    prod.published = 'PV'
    prod.save()
    return HttpResponseRedirect(reverse_lazy('prod', kwargs={'pk': new_pk}))


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
            item = str(self.get_object().id)
            if account.saved_services:
                if item not in account.saved_services.split(', '):
                    account.saved_services += ', ' + item
            else:
                account.saved_services += item
            account.save()
        return HttpResponseRedirect(success_url)


class ServicesView(ListView):
    """View for entering details to purchase a service."""

    template_name = 'services.html'
    model = Service
    success_url = reverse_lazy('servs')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ServicesView, self).get_context_data(**kwargs)
        context['servs'] = self.model.objects.filter(published='PB')
        set_basic_context(context, 'servs')
        return context


class CreateProductView(UserPassesTestMixin, CreateView):
    """View for creating a product."""

    template_name = 'create_product.html'
    model = Product
    success_url = reverse_lazy('prods')
    form_class = ProductForm

    def test_func(self):
        """Validate access."""
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CreateView, self).get_context_data(**kwargs)
        creator = context['form'].fields['creator']
        creator.queryset = User.objects.filter(is_staff=True)
        creator.initial = User.objects.get(username='m.ravenmoore')
        set_basic_context(context, 'add_prod')
        return context

    def form_valid(self, form):
        """Set date published if public."""
        if form.instance.published == 'PB':
            form.instance.date_published = datetime.now()
        return super(CreateProductView, self).form_valid(form)


class EditProductView(UserPassesTestMixin, UpdateView):
    """View for editing a product."""

    permission_required = ''
    template_name = 'edit_product.html'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('prods')

    def test_func(self):
        """Validate access."""
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(EditProductView, self).get_context_data(**kwargs)
        staff = User.objects.filter(is_staff=True)
        context['form'].fields['creator'].queryset = staff
        set_basic_context(context, 'prods')
        return context

    def form_valid(self, form):
        """Set date published if public."""
        if not form.instance.date_published:
            if form.instance.published == 'PB':
                form.instance.date_published = datetime.now()
        return super(EditProductView, self).form_valid(form)


class DeleteServiceView(DeleteView, UserPassesTestMixin):
    """Remove an existing product."""

    model = Service
    success_url = reverse_lazy('servs')
    template_name = 'delete_service.html'

    def test_func(self):
        """Validate access."""
        return self.request.user.is_staff


@login_required
@user_passes_test(valid_staff)
def copy_serv(request, pk):
    """Copy a service."""
    serv = Service.objects.get(pk=pk)
    new_pk = Service.objects.last().pk + 1
    serv.pk = new_pk
    serv.name += ' Copy'
    serv.published = 'PV'
    serv.save()
    return HttpResponseRedirect(reverse_lazy('serv', kwargs={'pk': new_pk}))


class CreateServiceView(UserPassesTestMixin, CreateView):
    """View for creating black smith services."""

    permission_required = ''
    template_name = 'create_service.html'
    model = Service
    success_url = reverse_lazy('servs')
    form_class = ServiceForm

    def test_func(self):
        """Validate access."""
        return self.request.user.is_staff

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


class EditServiceView(UserPassesTestMixin, UpdateView):
    """View for editing a product."""

    permission_required = ''
    template_name = 'edit_service.html'
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy('servs')

    def test_func(self):
        """Validate access."""
        return self.request.user.is_staff

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


class QuoteView(FormView):
    """Form to contact the shop."""

    template_name = 'quote.html'
    form_class = QuoteForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(QuoteView, self).get_context_data(**kwargs)
        names = []
        for serv in Service.objects.filter(published='PB'):
            names.append((serv.name, serv.name))
        context['form'].fields['service'].choices = names
        set_basic_context(context, 'quote')
        return context

    def post(self, request, *args, **kwargs):
        """Send email with conact info."""
        form = QuoteForm(request.POST)
        if form.is_valid():
            subject = 'Service Request: ' + form.cleaned_data['service']
            body = '''
{} {} is interested in requesting the service for {}.
Their contact info includes:

    Home Phone: {}
'''.format(
                form.cleaned_data['first_name'],
                form.cleaned_data['last_name'],
                form.cleaned_data['service'],
                form.cleaned_data['home_phone'],
            )
            if form.cleaned_data['cell_phone']:
                body += '''
    Cell Phone: {}
'''.format(
                    form.cleaned_data['cell_phone']
                )
            body += '''
    Email: {}
'''.format(
                form.cleaned_data['email'],
            )
            if form.cleaned_data['address']:
                body += '''
    Address: {}
'''.format(
                    form.cleaned_data['address']
                )
            if form.cleaned_data['city']:
                body += '''
    City: {}
'''.format(
                    form.cleaned_data['city']
                )
            if form.cleaned_data['state']:
                body += '''
    State: {}
'''.format(
                    form.cleaned_data['state']
                )
            body += '''
    Zip Code: {}
'''.format(
                form.cleaned_data['zip_code']
            )
            if form.cleaned_data['description']:
                body += '''
They have included the following description:

{}
'''.format(
                    form.cleaned_data['description']
                )
            if request.FILES:
                body += '''
and the attached images.'''
            quote = EmailMessage(subject, body, 'rvfmsite@gmail.com',
                                 ['Creations@ravenvfm.com'])
            if request.FILES:
                for image in request.FILES.values():
                    quote.attach(image.name, image.read(), image.content_type)
            quote.send(fail_silently=True)
            return HttpResponseRedirect(self.success_url)


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
            total = account.cart_total
            pre_order_total = account.pre_order_total
        if 'shipping_data' in session.keys():
            if session['shipping_data'] == 'in_store':
                context['in_store'] = True
            else:
                context['shipping'] = session['shipping_data']['shipping']
                context['info'] = session['shipping_data']['info']
                if 'exists' in session['shipping_data'].keys():
                    context['ship_exists'] = session['shipping_data']['exists']
        elif self.request.user.is_authenticated:
            context['shipping'] = info.get(pk=account.main_address)
            context['info'] = {'first': account.first_name,
                               'last': account.last_name,
                               'email': self.request.user.email}
        if self.request.user.is_anonymous:
            if not session.get_expire_at_browser_close():
                session.set_expiry(0)
            if 'account' not in session.keys():
                session['account'] = {
                    'cart': '',
                    'cart_total': 0.0,
                    'pre_order': '',
                    'pre_order_total': 0.0,
                }
            cart = session['account']['cart']
            pre_order = session['account']['pre_order']
            context['account'] = session['account']
            total = session['account']['cart_total']
            pre_order_total = session['account']['pre_order_total']
        else:
            cart = account.cart
            pre_order = account.pre_order
            if len(context['account'].shippinginfo_set.values()) > 1:
                addresses = context['account'].shippinginfo_set.values()
                context['alt_add'] = [address for address in addresses]
        if cart:
            context['cart'] = unpack(cart)
        if pre_order:
            context['pre_order'] = unpack(pre_order)
        context['item_fields'] = ['color', 'length', 'diameter', 'extras']
        context['total'] = Decimal(str(float("%.2f" % (total))))
        context['pre_order_total'] = Decimal(str(float("%.2f" % (pre_order_total))))
        if str(context['total'])[-2] == '.':
            context['total'] = Decimal(
                str(context['total']) + '0'
            )
        if str(context['pre_order_total'])[-2] == '.':
            context['pre_order_total'] = Decimal(
                str(context['pre_order_total']) + '0'
            )
        set_basic_context(context, 'cart')
        return context

    def post(self, request, *args, **kwargs):
        """Apply shipping info for guest user."""
        data = request.POST
        exists = False
        field_count = 0
        if 'in_store' in data.keys():
            request.session['shipping_data'] = 'in_store'
            request.session.save()
            return HttpResponseRedirect(self.success_url)
        ship_fields = ['ship_first_name', 'ship_last_name', 'ship_email',
                       'ship_add_1', 'ship_city', 'ship_state', 'ship_zip']
        if 'ship_first_name' in data.keys():
            if request.user.is_authenticated:
                account = Account.objects.get(user=request.user)
                exists = check_address(data, account)
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
        if exists:
            request.session['shipping_data']['exists'] = exists
            request.session.save()
        if field_count == 7:
            return HttpResponseRedirect(self.success_url)
        return HttpResponseRedirect(reverse_lazy('cart'))


def update_cart(request):
    """Change quantity of items in cart and update total."""
    item_id = request.GET['item_id']
    target_type = request.GET['type']
    if request.user.is_authenticated:
        if target_type != 'pre':
            target = unpack(request.user.account.cart)
            target_total = request.user.account.cart_total
        else:
            target = unpack(request.user.account.pre_order)
            target_total = request.user.account.pre_order_total
    else:
        if target_type != 'pre':
            target = unpack(request.session['account']['cart'])
            target_total = Decimal(request.session['account']['cart_total'])
        else:
            target = unpack(request.session['account']['pre_order'])
            target_total = request.session['account']['pre_order_total']
    prods = []
    prod_idx = None
    for idx, item in enumerate(target):
        prods.append(item)
        if item['item_id'] == int(item_id):
            prod_idx = idx
    difference = (int(request.GET['quantity']) -
                  int(prods[prod_idx]['quantity']))
    price = prods[prod_idx]['item'].price
    if 'extras' in prods[prod_idx].keys():
        price += Decimal(prods[prod_idx]['extras'].split(' $')[1])
    target_total += Decimal(price * difference)
    prods[prod_idx]['quantity'] = request.GET['quantity']
    cart_repack(prods, request, target_total, target_type)
    return HttpResponse(target_total)


def delete_item(request):
    """Remove items from cart or preorder and update total."""
    item_id = request.GET['item']
    del_type = request.GET['type']
    if request.user.is_authenticated:
        if del_type != 'pre':
            target = unpack(request.user.account.cart)
            target_total = request.user.account.cart_total
        else:
            target = unpack(request.user.account.pre_order)
            target_total = request.user.account.pre_order_total
    else:
        if del_type == 'pre':
            target = unpack(request.session['account']['pre_order'])
            target_total = request.session['account']['pre_order_total']
        else:
            target = unpack(request.session['account']['cart'])
            target_total = Decimal(request.session['account']['cart_total'])
    prods = []
    prod_idx = None
    for idx, item in enumerate(target):
        prods.append(item)
        if item['item_id'] == int(item_id):
            prod_idx = idx
    if len(prods) == 1:
        target_total = Decimal(0.0)
        if del_type == 'pre':
            if request.user.is_authenticated:
                request.user.account.pre_order_total = target_total
                request.user.account.pre_order = ''
                request.user.account.save()
            else:
                request.session['account']['pre_order_total'] = target_total
                request.session['account']['pre_order'] = ''
                request.session.save()
            return HttpResponse('empty')
        else:
            if request.user.is_authenticated:
                request.user.account.cart_total = target_total
                request.user.account.cart = ''
                request.user.account.save()
            else:
                request.session['account']['cart_total'] = target_total
                request.session['account']['cart'] = ''
                request.session.save()
            return HttpResponse('empty')
    price = prods[prod_idx]['item'].price
    if 'extras' in prods[prod_idx].keys():
        price += Decimal(prods[prod_idx]['extras'].split(' $')[1])
    target_total -= Decimal(price * int(prods[prod_idx]['quantity']))
    prods.pop(prod_idx)
    cart_repack(prods, request, target_total, del_type)
    return HttpResponse(target_total)


def apply_discount(request):
    """Apply a discount code to current order."""
    code = request.GET['code']
    try:
        discount = Discount.objects.get(code=code)
    except:
        return HttpResponse("<div id='message' class='w-100'><p class='text-standard'>\
    Not a valid discount code.</p></div>")
    if not discount.code_state:
        return HttpResponse("<div id='message' class='w-100'><p class='text-standard'>\
    Not an active discount code.</p></div>")
    if 'code' not in request.session.keys():
        request.session['code'] = code
        request.session.save()
        if request.user.is_authenticated:
            request.user.account.active_code = code
            request.user.account.save()
    return HttpResponse("<p class='text-standard'>Discount \
code activated!</p>")


def remove_discount(request):
    """Remove currently active discount code."""
    request.session.pop('code', None)
    request.session.save()
    if request.user.is_authenticated:
        request.user.account.active_code = ''
        request.user.account.save()
    return HttpResponse("<div class='col'><p class='text-standard'>\
Discount code removed refresh the page to add a new code.</p></div>")


def create_payment(request):
    """Create payment with paypal API."""
    paypalrestsdk.configure({
        "mode": os.environ.get('PAYPAL_MODE'),
        "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
        "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET')})

    base_url = request.get_raw_uri().split('create')[0]
    session = request.session
    if request.user.is_authenticated:
        cart = request.user.account.cart
        pre_order = request.user.account.pre_order
    else:
        cart = session['account']['cart']
        pre_order = session['account']['pre_order']
    if cart:
        cart = unpack(cart)
    if pre_order:
        pre_order = unpack(pre_order)
    items = []
    shipping_discount = 0
    item_count = 0
    for item in cart:
        item_count += int(item['quantity'])
    for item in cart:
        obj = Product.objects.get(id=item['item_id'])
        price = obj.price
        if 'code' in session.keys():
            discount = Discount.objects.get(code=session['code'])
            amount = discount.value
            if '$' in amount:
                percent = Decimal(amount[1:]) / item_count
                price -= percent
            elif 'ship' in amount:
                if 'free' in amount:
                    shipping_discount = session['paypal']['shipping']
                else:
                    shipping_discount = Decimal(amount[5:])
            else:
                percent = Decimal(float(price)) * Decimal('.' + amount[:-1])
                price -= percent
        if request.session['shipping_data'] == 'in_store':
            price = Decimal(float(price)) / Decimal('10')
        prod = {
            "name": obj.name,
            "description": item["description"],
            "price": str(price),
            "currency": "USD",
            "quantity": item["quantity"]
        }
        items.append(prod)
    for item in pre_order:
        item_count += int(item['quantity'])
    for item in pre_order:
        obj = Product.objects.get(id=item['item_id'])
        price = obj.price
        if 'code' in session.keys():
            discount = Discount.objects.get(code=session['code'])
            amount = discount.value
            if '$' in amount:
                percent = Decimal(amount[1:]) / item_count
                price -= percent
            elif 'ship' in amount:
                if 'free' in amount:
                    shipping_discount = session['paypal']['shipping']
                else:
                    shipping_discount = Decimal(amount[5:])
            else:
                percent = Decimal(float(price)) * Decimal('.' + amount[:-1])
                price -= percent
        if request.session['shipping_data'] == 'in_store':
            price = Decimal(float(price)) / Decimal('10')
        prod = {
            "name": obj.name,
            "description": item["description"],
            "price": str(price),
            "currency": "USD",
            "quantity": item["quantity"]
        }
        items.append(prod)
    pay_pal_total = session['paypal']['total']
    pay_pal_subtotal = session['paypal']['subtotal']
    pay_pal_tax = session['paypal']['tax']
    if request.session['shipping_data'] == 'in_store':
        pay_pal_total = Decimal(float(pay_pal_total)) / Decimal('10')
        pay_pal_subtotal = Decimal(float(pay_pal_subtotal)) / Decimal('10')
        pay_pal_tax = Decimal(float(pay_pal_tax)) / Decimal('10')
    if '.' not in str(shipping_discount):
        shipping_discount = str(shipping_discount) + '.00'
    elif str(shipping_discount)[-2] == '.':
        shipping_discount = str(shipping_discount) + '0'
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": base_url + "checkout-complete/",
            "cancel_url": base_url + "checkout/"},
        "transactions": [{
            "item_list": {
                "items": items
            },
            "amount": {
                "total": str(pay_pal_total),
                "currency": "USD",
                "details": {
                    "subtotal": str(pay_pal_subtotal),
                    "tax": str(pay_pal_tax),
                    "shipping": session['paypal']['shipping'],
                    "shipping_discount": str(shipping_discount),
                }
            },
            "description": "Payment for goods to Ravenmoore Valley \
 Forge and Metalworks."}]})
    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                create_order(request)
                return redirect(approval_url)
    else:
        print(payment.error)
        return redirect(base_url + "cart/")


def create_order(request):
    """Create an order during payment processing."""
    shipping_data = ''
    address = ''
    if request.user.is_authenticated:
        user = request.user
        account = request.user.account
        cart = account.cart
    else:
        user = User.objects.get(username='Guest')
        account = Account.objects.get(user=user)
        cart = request.session['account']['cart']
    shipping_data = request.session['shipping_data']
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
        address.resident = Account.objects.get(user=user)
        if request.user.is_authenticated:
            address.name = 'Saved address ' + str(
                len(ShippingInfo.objects.filter(resident=account)) + 1
            )
        address.save()
    email = shipping_data['info']['email']
    name = (shipping_data['info']['first'] +
            ', ' + shipping_data['info']['last'])
    order = Order(
        buyer=account,
        order_content=cart,
        recipient_email=email,
        recipient=name,
        ship_to=address,
    )
    order.save()
    request.session['order_num'] = order.id
    request.session.save()


class CheckoutView(TemplateView):
    """Checkout page renders tax and shipping for order before payment."""

    template_name = 'checkout.html'
    success_url = reverse_lazy('create_payment')

    def get(self, request, *args, **kwargs):
        """Handle redirects when missing context."""
        session = request.session
        keys = session.keys()
        view = CheckoutView
        if 'shipping_data' not in keys:
            return HttpResponseRedirect(reverse_lazy('cart'))
        if session['shipping_data'] == 'in_store':
            return super(view, self).get(self, request, *args, **kwargs)
        field_count = 0
        ship_fields = ['address1', 'city', 'state', 'zip_code']
        info_fields = ['first', 'last', 'email']
        for i in ship_fields:
            if session['shipping_data']['shipping'][i]:
                field_count += 1
        for i in info_fields:
            if session['shipping_data']['info'][i]:
                field_count += 1
        if field_count < 7:
            return HttpResponseRedirect(reverse_lazy('cart'))
        return super(view, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Define context for checkout view."""
        context = super(CheckoutView, self).get_context_data(**kwargs)
        session = self.request.session
        cart = None
        pre_order = None
        in_store = False
        if session['shipping_data'] != 'in_store':
            context['shipping'] = session['shipping_data']['shipping']
            context['info'] = session['shipping_data']['info']
        else:
            in_store = True
            context['in_store'] = True
        if self.request.user.is_authenticated:
            account = self.request.user.account
            if account.active_code:
                self.request.session['code'] = account.active_code
                context['code'] = account.active_code
            context['account'] = account
            pre_order = account.pre_order
            pre_order_total = account.pre_order_total
            total = account.cart_total
            cart = account.cart
            if len(account.shippinginfo_set.values()) > 1:
                addresses = account.shippinginfo_set.values()
                context['alt_add'] = [address for address in addresses]
        else:
            context['account'] = session['account']
            cart = context['account']['cart']
            total = context['account']['cart_total']
            pre_order = context['account'].pre_order
            pre_order_total = context['account'].pre_order_total
            if not session.get_expire_at_browser_close():
                session.set_expiry(0)
        shipping_cost = 0
        if not in_store:
            zip_code = session['shipping_data']['shipping']['zip_code']
            street = session['shipping_data']['shipping']['address1']
            tax_rate = taxjar_client.rates_for_location(
                zip_code,
                {'street': street}
            )['combined_rate']
            info = session['shipping_data']['info']
            shipping = session['shipping_data']['shipping']
            name = info['first'] + ' ' + info['last']
            state = get_state(shipping['state'])
            to_address = easypost.Address.create(
                name=name,
                street1=shipping['address1'],
                street2=shipping['address2'],
                city=shipping['city'],
                state=state,
                zip=shipping['zip_code'],
                country='US',
                email=info['email']
            )
            from_address = easypost.Address.create(
                name='RVFM Shop',
                street1='11639 13th Ave SW',
                city='Burien',
                state='WA',
                zip='98146',
                country='US',
                phone='2063726501',
                email='Creations@ravenvfm.com'
            )
            if cart:
                context['cart'] = unpack(cart)
                for item in context['cart']:
                    parcel = easypost.Parcel.create(
                        length=item['item'].shipping_length,
                        width=item['item'].shipping_width,
                        height=item['item'].shipping_height,
                        weight=item['item'].shipping_weight
                    )
                    shipment = easypost.Shipment.create(
                        to_address=to_address,
                        from_address=from_address,
                        parcel=parcel,
                    )
                    rate_price = shipment.lowest_rate()['rate']
                    shipping_cost += (
                        float(rate_price) * float(item['quantity'])
                    )
            if pre_order:
                context['pre_order'] = unpack(pre_order)
                for item in context['pre_order']:
                    parcel = easypost.Parcel.create(
                        length=item['item'].shipping_length,
                        width=item['item'].shipping_width,
                        height=item['item'].shipping_height,
                        weight=item['item'].shipping_weight
                    )
                    shipment = easypost.Shipment.create(
                        to_address=to_address,
                        from_address=from_address,
                        parcel=parcel,
                    )
                    rate_price = shipment.lowest_rate()['rate']
                    shipping_cost += (
                        float(rate_price) * float(item['quantity'])
                    )
        else:
            tax_rate = taxjar_client.rates_for_location(
                '98146',
                {'street': '11639 13th Ave SW'}
            )['combined_rate']
        context['tax_rate'] = float("%.2f" % (tax_rate * 100))
        context['shipping_cost'] = float("%.2f" % (shipping_cost))
        context['subtotal'] = total
        context['pre_subtotal'] = pre_order_total
        if 'code' in session.keys():
            discount = Discount.objects.get(code=session['code'])
            if discount.code_state:
                amount = discount.value
                if discount.prod:
                    effected_prod = Product.objects.get(id=discount.prod)
                    cart_effect = False
                    pre_order_effect = False
                    if cart:
                        for item in unpack(cart):
                            if item['item'] == effected_prod:
                                cart_effect = True
                                effected_quantity = item['quantity']
                    if pre_order:
                        for item in unpack(pre_order):
                            if item['item'] == effected_prod:
                                pre_order_effect = True
                                effected_quantity = item['quantity']
                    if not cart_effect and not pre_order_effect:
                        effect = "You have no orders of {} in your cart, \
no effect from".format(effected_prod.name)
                    else:
                        if '$' in amount:
                            effect = amount
                            context['discount'] = Decimal(amount[1:]) * effected_quantity
                            if cart_effect:
                                context['subtotal'] -= context['discount']
                            else:
                                context['pre_subtotal'] -= context['discount']
                        elif 'ship' in amount:
                            if 'free' in amount:
                                effect = 'Free Shipping'
                                context['shipping_cost'] = 0
                            else:
                                value = amount[5:]
                                effect = '${} off shipping'
                                context['shipping_cost'] -= Decimal(value)
                        else:
                            effect = discount.value + '%'
                            percent = Decimal(float(effected_prod.price)) * Decimal('.' + amount)
                            context['discount'] = percent * int(effected_quantity)
                            if cart_effect:
                                context['subtotal'] -= context['discount']
                            else:
                                context['pre_subtotal'] -= context['discount']
                        effect += ' off {}x {}'.format(
                            effected_quantity, effected_prod.name
                        )
        context['total'] = (
            context['subtotal'] +
            Decimal(str(context['shipping_cost'])) +
            context['pre_subtotal']
        )
        if 'code' in session.keys():
            discount = Discount.objects.get(code=session['code'])
            if discount.code_state:
                amount = discount.value
                if not discount.prod:
                    if '$' in amount:
                        effect = amount
                        context['discount'] = Decimal(amount[1:])
                        context['total'] -= context['discount']
                    elif 'ship' in amount:
                        if 'free' in amount:
                            effect = 'Free Shipping'
                            context['shipping_cost'] = 0
                        else:
                            value = amount[5:]
                            effect = '${} off shipping'
                            context['shipping_cost'] -= Decimal(value)
                    else:
                        effect = discount.value + '%'
                        context['discount'] = Decimal(float(context['total'])) * Decimal('.' + amount)
                        context['total'] -= context['discount']
            context['code'] = [discount.code, effect]
        tax = Decimal(str(tax_rate)) * context['total']
        context['tax'] = Decimal(str(float("%.2f" % (tax))))
        context['total'] += context['tax']
        fields = ['subtotal', 'shipping_cost',
                  'tax', 'total', 'pre_subtotal']
        for field in fields:
            if str(context[field])[-2] == '.':
                context[field] = Decimal(str(context[field]) + '0')
        set_basic_context(context, 'cart')
        session['paypal'] = {
            'subtotal': str(context['subtotal'] + context['pre_subtotal']),
            'total': str(context['total']),
            'tax': str(context['tax']),
            'shipping': str(context['shipping_cost'])
        }
        session.save()
        context['deposit'] = str(round(context['total'] / 10, 2))
        return context

    def post(self, request, *args, **kwargs):
        """Apply shipping info for guest user."""
        session = request.session
        if session['shipping_data'] == 'in_store':
            return HttpResponseRedirect(self.success_url)
        field_count = 0
        ship_fields = ['address1', 'city', 'state', 'zip_code']
        info_fields = ['first', 'last', 'email']
        for i in ship_fields:
            if session['shipping_data']['shipping'][i]:
                field_count += 1
        for i in info_fields:
            if session['shipping_data']['info'][i]:
                field_count += 1
        if field_count == 7:
            return HttpResponseRedirect(self.success_url)
        return HttpResponseRedirect(reverse_lazy('cart'))


class CheckoutCompleteView(TemplateView):
    """Checkout complete page, shifts cart to history and resets."""

    template_name = 'checkout_complete.html'

    def get(self, request, *args, **kwargs):
        """Check for shipping data."""
        keys = request.session.keys()
        view = CheckoutCompleteView
        if 'shipping_data' not in keys:
            return HttpResponseRedirect(reverse_lazy('cart'))
        payment_id = request.GET['paymentId']
        payment = paypalrestsdk.Payment.find(payment_id)
        payer_id = request.GET['PayerID']
        if payment.execute({"payer_id": payer_id}):
            verify_payment = paypalrestsdk.Payment.find(payment_id)
            if verify_payment:
                order = Order.objects.get(id=request.session['order_num'])
                order.paid = True
                order.save()
                items = unpack(order.order_content)
                for item in items:
                    if item['item'].stock:
                        item['item'].stock -= int(item['quantity'])
                        if item['item'].stock == 0:
                            # TO-DO: send matt an email for out of stock
                            pass
                    item['item'].save()
                return super(view, self).get(self, request, *args, **kwargs)
        return HttpResponseRedirect(reverse_lazy('cart'))

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CheckoutCompleteView, self).get_context_data(**kwargs)
        session = self.request.session
        context['order'] = session['order_num']
        if self.request.user.is_authenticated:
            account = self.request.user.account
            cart = split_cart(account.cart)
        else:
            cart = split_cart(session['account']['cart'])
        email = 'rvfmsite@gmail.com'
        subject = 'Order #{} Confirmation'.format(context['order'])
        info = session['shipping_data']['info']
        # Add in shipping info if matt wants that in the email.
        name = info['first'] + ', ' + info['last']
        owner_body = 'Purchased items:\n'
        client_body = 'You will recieve an email with tracking info \
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
                                   email,
                                   ['Creations@ravenvfm.com'])
        client_email = EmailMessage(subject,
                                    client_body,
                                    email,
                                    [info['email']])
        owner_email.send(fail_silently=True)
        client_email.send(fail_silently=True)
        session_keys = [
            'shipping_data', 'code', 'paypal', 'order_num'
        ]
        for item in session_keys:
            try:
                del session[item]
            except KeyError:
                pass
        session.save()
        if self.request.user.is_authenticated:
            account.cart = ''
            account.cart_total = 0.0
            account.active_code = ''
            account.save()
        else:
            session['account'] = {'cart': '', 'cart_total': 0.0}
            session.save()
        set_basic_context(context, 'cart')
        return context


def check_address(data, account):
    """Check if user is using an existing address."""
    types_data = {
        'ship_address_name': ['ship_add_1', 'ship_add_2',
                              'ship_city', 'ship_state', 'ship_zip'],
    }
    if 'ship_address_name' in data.keys():
        add_id = data['ship_address_name'].split(', ')[0].split(': ')[1]
        address = ShippingInfo.objects.get(id=add_id)
    else:
        address = ShippingInfo.objects.get(resident=account)
    types_data['address'] = [address.address1, address.address2,
                             address.city, address.state, address.zip_code]
    equal = 0
    for idx, item in enumerate(types_data['ship_address_name']):
        if data[item] == types_data['address'][idx]:
            equal += 1
    if equal == 5:
        return address.id


def cart_repack(prods, request, total, pack_type):
    """Repack items into the cart."""
    repack = ''
    for i in prods:
        i.pop('item')
        if repack:
            repack += '|' + json.dumps(i)
        else:
            repack += json.dumps(i)
    if pack_type == 'cart':
        if request.user.is_authenticated:
            request.user.account.cart = repack
            request.user.account.cart_total = total
            request.user.account.save()
        else:
            request.session['account']['cart'] = repack
            request.session['account']['total'] = str(total)
            request.session.save()
    else:
        if request.user.is_authenticated:
            request.user.account.pre_order = repack
            request.user.account.pre_order_total = total
            request.user.account.save()
        else:
            request.session['account']['pre_order'] = repack
            request.session['account']['pre_order_total'] = str(total)
            request.session.save()
