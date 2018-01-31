"""."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from registration.backends.hmac.views import RegistrationView
from registration.forms import RegistrationForm
from account.models import Account, ShippingInfo
from catalog.models import Product, Service
from account.forms import InfoRegForm, AddAddressForm
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login
from RVFS.google_drive import main as drive_files
from RVFS.google_calendar import create_event
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import os
import random
import json


MONTHS = {
    'January': '01',
    'Febuary': '02',
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


class HomeView(TemplateView):
    """Home View."""

    template_name = 'rvfsite/home.html'

    def get_context_data(self, **kwargs):
        """."""
        slide_files = drive_files('17fqQwUu1dGPOUBirLDo2O0tBg_TUXMlZ')
        rand_pics = random.sample(slide_files, min(5, len(slide_files)))
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
        context['random_pics'] = rand_pics
        context['galleries'] = get_galleries()
        context['nbar'] = 'home'
        return context


class AboutView(TemplateView):
    """About View."""

    template_name = 'rvfsite/about.html'

    def get_context_data(self, **kwargs):
        """."""
        context = super(TemplateView, self).get_context_data(**kwargs)
        try:
            context['matt'] = User.objects.get(username='m.ravenmoore').account
        except ObjectDoesNotExist:
            pass
        try:
            context['becky'] = User.objects.get(username='b.ravenmoore').account
        except ObjectDoesNotExist:
            pass
        try:
            context['gordon'] = User.objects.get(username='gordon').account
        except ObjectDoesNotExist:
            pass
        context['isis'] = os.path.join(settings.STATIC_URL, 'isis.jpg')
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'about'
        return context


class AccountView(LoginRequiredMixin, ListView):
    """Custom geistration view."""

    template_name = 'account.html'
    model = Account

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        context['account'] = context['view'].request.user.account
        context['address'] = ShippingInfo.objects.get(pk=context['account'].main_address)
        if context['account'].cart:
            context['cart'] = unpack(context['account'].cart)
        if context['account'].saved_products:
            context['saved_prods'] = unpack(context['account'].saved_products)
        if context['account'].saved_services:
            context['saved_servs'] = unpack(context['account'].saved_services)
        if context['account'].purchase_history:
            context['prod_history'] = unpack(context['account'].purchase_history)
        if context['account'].service_history:
            context['serv_history'] = unpack(context['account'].service_history)
        context['item_fields'] = ['quantity', 'color', 'length', 'diameter', 'extras']
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'account'
        return context


class AddAddressView(LoginRequiredMixin, CreateView):
    """Add a shipping address."""

    template_name = 'add_address.html'
    model = ShippingInfo
    success_url = reverse_lazy('account')
    form_class = AddAddressForm

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(AddAddressView, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'account'
        return context

    def form_valid(self, form):
        """Verify the fields and adjust account values."""
        info = form.save(commit=False)
        account = self.request.user.account
        info.resident = account
        info.state = form.cleaned_data['state']
        info.save()
        if info.main:
            old_main = ShippingInfo.objects.get(pk=account.main_address)
            old_main.main = False
            old_main.save()
            account.main_address = info.id
            if len(account.shippinginfo_set.all()) > 1:
                account.has_address_delete = True
        account.save()
        return super(AddAddressView, self).form_valid(form)


class AddressListView(LoginRequiredMixin, ListView):
    """Change your main shipping address."""

    template_name = 'change_address.html'
    model = ShippingInfo
    success_url = reverse_lazy('account')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(AddressListView, self).get_context_data(**kwargs)
        account = context['view'].request.user.account
        context['account'] = account
        context['addresses'] = ShippingInfo.objects.filter(resident=account)
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'account'
        return context

    def post(self, request, *args, **kwargs):
        """Change out main address."""
        data = request.POST
        for key in data.keys():
            if key.startswith('main'):
                add_key = key
        add_id = add_key.split(' ')[1]
        account = request.user.account
        old_main = account.main_address
        address = ShippingInfo.objects.get(pk=old_main)
        address.main = False
        address.save()
        account.main_address = add_id
        new_add = ShippingInfo.objects.get(pk=add_id)
        new_add.main = True
        new_add.save()
        account.save()
        return HttpResponseRedirect(self.success_url)


class DeleteAddress(LoginRequiredMixin, DeleteView):
    """Delete an address."""

    permission_required = 'account.has_address_delete'
    model = ShippingInfo
    success_url = reverse_lazy('account')
    template_name = 'del_add.html'

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(DeleteAddress, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'account'
        return context

    def post(self, request, *args, **kwargs):
        """Change out main address."""
        info = ShippingInfo.objects.get(pk=kwargs['pk'])
        info.delete()
        account = request.user.account
        if len(account.shippinginfo_set.all()) == 1:
            account.has_address_delete = False
        account.save()
        return HttpResponseRedirect(self.success_url)


class EditAccountView(LoginRequiredMixin, DetailView):
    """Edit view for the account."""

    template_name = 'edit_account.html'
    model = Account
    success_url = reverse_lazy('account')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(EditAccountView, self).get_context_data(**kwargs)
        account = context['view'].request.user.account
        context['address'] = ShippingInfo.objects.get(pk=account.main_address)
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'account'
        return context

    def post(self, request, *args, **kwargs):
        """Add item to appropriate list."""
        data = request.POST, request.FILES
        account = Account.objects.get(user=request.user)
        if 'birthday' in data[0].keys():
            bday = validate_bday(data[0]['birthday'])
            if bday:
                account.birth_day = bday
        if 'first_name' in data[0].keys():
            account.first_name = data[0]['first_name']
        if 'last_name' in data[0].keys():
            account.last_name = data[0]['last_name']
        if 'pic' in data[1].keys():
            account.pic = data[1]['pic']
        account.save()
        info = ShippingInfo.objects.get(pk=account.main_address)
        if 'state' in data[0].keys():
            info.state = data[0]['state']
        if 'city' in data[0].keys():
            info.city = data[0]['city']
        if 'address1' in data[0].keys():
            info.address1 = data[0]['address1']
        if 'address2' in data[0].keys():
            info.address2 = data[0]['address2']
        if 'zip_code' in data[0].keys():
            info.zip_code = data[0]['zip_code']
        info.save()
        return HttpResponseRedirect(self.success_url)


class CustomRegView(RegistrationView):
    """Custom regeistration view."""

    form_class = RegistrationForm
    model = User

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(RegistrationView, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'register'
        return context


class CustomLogView(LoginView):
    """Custom login view."""

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(LoginView, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'login'
        return context

    def form_valid(self, form):
        """Validate if user has finished extra registration."""
        user = User.objects.get(username=form.data['username'])
        account = Account.objects.get(user=user)
        if account:
            if account.registration_complete:
                auth_login(self.request, form.get_user())
                return HttpResponseRedirect(self.get_success_url())
            else:
                return redirect('info_reg', pk=account.pk)


class InfoFormView(UpdateView):
    """Form for shipping info and birthday."""

    template_name = 'info-form.html'
    form_class = InfoRegForm
    success_url = '/account'
    model = Account

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(InfoFormView, self).get_context_data(**kwargs)
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['nbar'] = 'login'
        return context

    def form_valid(self, form):
        """Creating shipping model and update user account."""
        user = User.objects.get(username=self.object.user.username)
        account = form.save(commit=False)
        if account.registration_complete:
            return HttpResponseRedirect(self.get_success_url())
        account.birthday_set = True
        account.save()
        # google calendar birthday add
        event = {}
        event['full_name'] = account.first_name + account.last_name
        event['time'] = account.birth_day
        event['birthday'] = 'True'
        event['length'] = 2400
        new_info = ShippingInfo()
        new_info.address1 = form.cleaned_data['street']
        if form.cleaned_data['adr_extra']:
            new_info.address2 = form.cleaned_data['adr_extra']
        new_info.zip_code = form.cleaned_data['zip_code']
        new_info.city = form.cleaned_data['city']
        new_info.state = form.cleaned_data['state']
        new_info.name = form.cleaned_data['location_name']
        new_info.main = True
        new_info.save()
        new_info.resident = account
        account.main_address = new_info.id
        account.registration_complete = True
        account.save()
        new_info.save()
        auth_login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())


class GalleryView(TemplateView):
    """Display the photos for a gallery."""

    template_name = 'gallery.html'

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(GalleryView, self).get_context_data(**kwargs)
        title = context['slug'].replace('_', ' ').title()
        context['cart_count'] = cart_count(self.request)
        context['galleries'] = get_galleries()
        context['tab'] = title
        context['gallery'] = title
        context['nbar'] = 'gallery'
        for file in context['galleries']:
            if file['name'].title() == title:
                folder = file['id']
        context['photos'] = drive_files(folder)
        for photo in context['photos']:
            photo['name'] = photo['name'].split('.')[0]
        return context


def get_galleries():
    """Fetch list of galleries from google drive."""
    files = drive_files('18HHO951sd6wkp_tCREzHQimX8ntwVycq')
    for file in files:
        file['url'] = file['name'].lower().replace(' ', '_')
    return files


def validate_bday(date):
    """Validate birthday structure."""
    date = date.split(' ')
    if len(date) != 3:
        return
    day = date[1][:-1]
    month = date[0]
    year = date[2]
    if len(year) != 4:
        return
    if len(day) > 2:
        return
    if len(day) == 1:
        day = '0' + day
    if month.title() not in MONTHS:
        return
    month = MONTHS[month.title()]
    return year + '-' + month + '-' + day


def cart_count(request):
    """Get current count of items in cart."""
    if not request.user.is_anonymous:
        cart = Account.objects.get(user=request.user).cart
        if cart:
            return len(cart.split('|'))
        return 0
    else:
        if 'account' in request.session.keys():
            if request.session['account']['cart']:
                return len(request.session['account']['cart'].split('|'))
        return 0


def unpack(packed_list):
    """Unpack the json saved cart/list."""
    items = []
    item_list = []
    unpacked = packed_list.split('|')
    for item in unpacked:
            items.append(json.loads(item))
    for item in items:
        if item['type'] == 'prod':
            item['item'] = Product.objects.get(pk=item['item_id'])
            item_list.append(item)
        else:
            item['item'] = Service.objects.get(pk=item['item_id'])
            item_list.append(item)
    return item_list


def split_cart(packed_list):
    """Split cart into servs and products."""
    items = {}
    unpacked = packed_list.split('|')
    for item in unpacked:
        if json.loads(item)['type'] == 'prod':
            if 'prods' in items.keys():
                items['prods'] += '|' + item
            else:
                items['prods'] = item
        if json.loads(item)['type'] == 'serv':
            if 'servs' in items.keys():
                items['servs'] += '|' + item
            else:
                items['servs'] = item
    return items
