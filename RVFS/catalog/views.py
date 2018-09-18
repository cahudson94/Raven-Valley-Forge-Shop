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
from account.views import unpack, split_cart, set_basic_context, valid_staff
from catalog.forms import ProductForm, ServiceForm, QuoteForm
from catalog.models import Product, Service
from datetime import datetime
from decimal import Decimal
import paypalrestsdk
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
            item_total = (Decimal(price) * Decimal(data['quantity']))
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
                                            item_total)
                self.request.session.save()
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
        context['form'].fields['Creator'].queryset = User.objects.filter(is_staff=True)
        context['form'].fields['Creator'].initial = User.objects.get(username='m.ravenmoore')
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
        context['api'] = os.environ.get('GOOGLE_API_KEY')
        set_basic_context(context, 'quote')
        return context

    def post(self, request, *args, **kwargs):
        """Send email with conact info."""
        form = QuoteForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            contact = EmailMessage(subject, message, from_email,
                                   ['rvfmsite@gmail.com'])
            # if files:
            #     for serv in servs:
            #         for file in serv['files'].split(', '):
            #             image = UserImage.objects.get(id=file.split(' ')[1])
            #             img_path = os.path.join(settings.BASE_DIR, 'media',
            #                                     image.image.name)
            #             owner_email.attach_file(img_path)
            contact.send(fail_silently=True)
            return HttpResponseRedirect(self.success_url)


class CartView(TemplateView):
    """Cart and checkout page."""

    template_name = 'cart.html'
    success_url = reverse_lazy('create_payment')

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
            for item in context['cart']:
                item['count'] = 'prod ' + str(len(context['prods']))
                context['prods'].append(item)
        context['item_fields'] = ['color', 'length', 'diameter', 'extras']
        set_basic_context(context, 'cart')
        return context

    def post(self, request, *args, **kwargs):
        """Apply shipping info for guest user."""
        data = request.POST
        exists = False
        field_count = 0
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
            shipping_data['exists'] = exists
        if field_count == 7:
            return HttpResponseRedirect(self.success_url)
        return HttpResponseRedirect(reverse_lazy('cart'))


def update_cart(request):
    """Change quantity of items in cart and update total."""
    cart_item = request.GET['cart_data'].split(' ')
    if request.user.is_authenticated:
        cart = unpack(request.user.account.cart)
        cart_total = request.user.account.cart_total
    else:
        cart = unpack(request.session['account']['cart'])
        cart_total = Decimal(request.session['account']['cart_total'])
    prods = []
    for item in cart:
        prods.append(item)
    if cart_item[0] == 'prod':
        difference = (int(request.GET['quantity']) -
                      int(prods[int(cart_item[1])]['quantity']))
        price = prods[int(cart_item[1])]['item'].price
        if 'extras' in prods[int(cart_item[1])].keys():
            price += Decimal(prods[int(cart_item[1])]['extras'].split(' $')[1])
        cart_total += Decimal(price * difference)
        prods[int(cart_item[1])]['quantity'] = request.GET['quantity']
    cart_repack(prods, request, cart_total)
    return HttpResponse(cart_total)


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
    for item in cart:
        prods.append(item)
    if len(prods) == 1:
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
    cart_total -= Decimal(prods[int(cart_item[1])]['item'].price *
                          int(prods[int(cart_item[1])]['quantity']))
    prods.pop(int(cart_item[1]))
    cart_repack(prods, request, cart_total)
    return HttpResponse(cart_total)


class CheckoutView(TemplateView):
    """Format order info to send to paypal."""

    template_name = 'checkout.html'

    def get(self, request, *args, **kwargs):
        """Check for shipping data."""
        keys = request.session.keys()
        if 'shipping_data' not in keys:
            return HttpResponseRedirect(reverse_lazy('cart'))
        return super(CheckoutView, self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        shipping_data = ''
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
        order = Order(
            buyer=account,
            order_content=cart,
            recipient_email=email,
            recipient=name,
        )
        order.save()
        order.ship_to = address
        order.save()
        self.request.session['order_num'] = order.id
        self.request.session['payment_id'] = self.request.GET['paymentId']
        self.request.session['payer_id'] = self.request.GET['PayerID']
        self.request.session.save()
        if shipping_data:
            context['shipping'] = address
            context['info'] = shipping_data['info']
        context['total'] = cart_total
        context['prods'] = []
        for item in unpack(cart):
            if item['type'] == 'prod':
                context['prods'].append(item)
        set_basic_context(context, 'cart')
        return context


def create_payment(request):
    """Create payment with paypal API."""
    paypalrestsdk.configure({
        "mode": os.environ.get('PAYPAL_MODE'),
        "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
        "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET')})

    base_url = request.get_raw_uri().split('create')[0]
    cart = unpack(request.user.account.cart)
    items = []
    total = 0
    for item in cart:
        if item['type'] == 'prod':
            obj = Product.objects.get(id=item['item_id'])
            price = obj.price
            total += price * Decimal(item["quantity"])
        else:
            obj = Service.objects.get(id=item['item_id'])
            if obj.commission_fee:
                price = Decimal(obj.commission_fee)
            else:
                price = Decimal(0)
            total += price
        prod_or_serv = {
            "name": obj.name,
            "description": item["description"],
            "price": str(price),
            "currency": "USD",
            "quantity": item["quantity"]
        }
        items.append(prod_or_serv)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": base_url + "checkout/",
            "cancel_url": base_url + "cart/"},
        "transactions": [{
            "item_list": {
                "items": items
            },
            "amount": {
                "total": str(total),
                "currency": "USD"},
            "description": "Payment for goods and or services to Ravenmoore\
 Valley Forge and Metalworks."}]})

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return redirect(approval_url)
    else:
        print(payment.error)
        return redirect(base_url + "cart/")


class CheckoutCompleteView(TemplateView):
    """Checkout complete page, shifts cart to history and resets."""

    template_name = 'checkout_complete.html'

    def get(self, request, *args, **kwargs):
        """Check for shipping data."""
        keys = request.session.keys()
        view = CheckoutCompleteView
        if 'shipping_data' not in keys:
            return HttpResponseRedirect(reverse_lazy('cart'))
        payment_id = request.session['payment_id']
        payment = paypalrestsdk.Payment.find(payment_id)
        payer_id = request.session['payer_id']
        if payment.execute({"payer_id": payer_id}):
            print('there')
            verify_payment = paypalrestsdk.Payment.find(payment_id)
            print(verify_payment)
            if verify_payment:
                order = Order.objects.get(id=request.session['order_num'])
                order.paid = True
                order.save()
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
                                   'rvfmsite@gmail.com',
                                   [email])
        client_email = EmailMessage(subject,
                                    client_body,
                                    email,
                                    [info['email']])
        owner_email.send(fail_silently=True)
        client_email.send(fail_silently=True)
        if self.request.user.is_authenticated:
            account.cart = ''
            account.cart_total = 0.0
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


def cart_repack(prods, request, cart_total):
    """Repack items into the cart."""
    cart_repack = ''
    for i in prods:
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
        request.session['account']['cart_total'] = str(cart_total)
        request.session.save()
