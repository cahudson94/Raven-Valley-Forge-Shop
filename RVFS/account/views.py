"""."""
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import (UpdateView, CreateView,
                                       DeleteView, FormView)
from account.forms import (InfoRegForm, AddAddressForm,
                           OrderUpdateForm, ContactForm)
from account.models import Account, ShippingInfo, SlideShowImage, Order
from catalog.models import Product, Service
from registration.backends.hmac.views import RegistrationView
from registration.forms import RegistrationForm
from RVFS.google_calendar import add_birthday, main as drive_files, download
import json
import os
import random


MONTHS = {
    'Jan.': '01',
    'Feb.': '02',
    'Mar.': '03',
    'Apr.': '04',
    'May': '05',
    'Jun.': '06',
    'Jul.': '07',
    'Aug.': '08',
    'Sep.': '09',
    'Oct.': '10',
    'Nov.': '11',
    'Dec.': '12',
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12',
    'January': '01',
    'Febuary': '02',
    'March': '03',
    'April': '04',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'
}


def valid_staff(self):
    """Validate access."""
    return self.is_staff


class HomeView(TemplateView):
    """Home View."""

    template_name = 'rvfsite/home.html'

    def get_context_data(self, **kwargs):
        """."""
        slides = set(SlideShowImage.objects.all())
        rand_pics = random.sample(slides, min(5, len(slides)))
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['random_pics'] = rand_pics
        set_basic_context(context, 'home')
        return context


@user_passes_test(valid_staff)
@login_required
def updateslideshow(request):  # pragma: no cover
    """Button to update the files of slide images."""
    slide_files = drive_files('17fqQwUu1dGPOUBirLDo2O0tBg_TUXMlZ')
    current_slides = SlideShowImage.objects.all()
    new_names = {}
    current_names = []
    for slide in slide_files:
        new_names[slide['name'].split('.')[0]] = slide
    for slide in current_slides:
        current_names.append(slide.name)
    for name in current_names:
        if name not in new_names:
            SlideShowImage.objects.get(name=name).delete()
    for name in new_names:
        if name not in current_names:
            new_image = SlideShowImage(
                image=SimpleUploadedFile(
                    name=name + '.jpg',
                    content=open(download(new_names[name]['id']), 'rb').read(),
                    content_type='image/jpeg'),
                name=name)
            new_image.save()
            file_path = os.path.join(settings.BASE_DIR, 'new_image.jpg')
            with open(file_path, 'w+') as file:
                file.write('')
    return HttpResponseRedirect(reverse_lazy('home'))


def newsletter(request):
    """Newsletter signup."""
    email = request.GET['email']
    if '@' not in email:
        return HttpResponseRedirect(reverse_lazy('home'))
    guest = User.objects.get(username='Guest')
    if guest.account.mailing_list:
        guest.account.mailing_list += ', ' + email
    else:
        guest.account.mailing_list = email
    guest.account.save()
    return HttpResponse("<p class='text-standard'>Thank you for \
signing up for the newsletter.</p>")


class AboutView(TemplateView):
    """About View."""

    template_name = 'rvfsite/about.html'

    def get_context_data(self, **kwargs):
        """."""
        context = super(TemplateView, self).get_context_data(**kwargs)
        staff = User.objects.filter(is_staff=True)
        groups = {}
        counter = 1
        for member in staff:
            if member.account.group not in groups and member.account.group:
                groups[member.account.group] = {member: counter}
                counter += 1
            elif member.account.group:
                groups[member.account.group][member] = counter
                counter += 1
        context['groups'] = groups
        context['count'] = counter
        context['isis'] = os.path.join(settings.STATIC_URL, 'isis.jpg')
        set_basic_context(context, 'about')
        return context


class AccountView(LoginRequiredMixin, ListView):
    """Custom geistration view."""

    template_name = 'account.html'
    model = Account

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        account = context['view'].request.user.account
        context['account'] = account
        main = context['account'].main_address
        context['address'] = ShippingInfo.objects.get(pk=main)
        if account.cart:
            context['cart'] = unpack(account.cart)
        if account.saved_products:
            context['saved_prods'] = [Product.objects.get(id=i) for i in
                                      account.saved_products.split(', ')]
        if account.saved_services:
            context['saved_servs'] = [Service.objects.get(id=i) for i in
                                      account.saved_services.split(', ')]
        orders = {}
        for order in Order.objects.filter(buyer=account):
            content = unpack(order.order_content, unpack_as="history")
            if content:
                orders[order.id] = content
        context['prod_history'] = orders
        context['item_fields'] = ['quantity',
                                  'color',
                                  'length',
                                  'diameter',
                                  'extras']
        set_basic_context(context, 'account')
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
        set_basic_context(context, 'account')
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
        set_basic_context(context, 'account')
        return context

    def post(self, request, *args, **kwargs):
        """Change out main address."""
        data = request.POST
        addresses = {}
        for key in data.keys():
            if key.isdigit():
                add_id = key
                addresses[key]['main'] = True
            elif key != 'csrfmiddlewaretoken':
                if key.split(' ')[1] in addresses.keys():
                    addresses[key.split(' ')[1]][key.split(' ')[0]] = data[key]
                else:
                    addresses[key.split(' ')[1]] = {}
                    addresses[key.split(' ')[1]][key.split(' ')[0]] = data[key]
        for key in addresses:
            if 'address2' not in addresses[key].keys():
                addresses[key]['address2'] = ''
            if 'main' not in addresses[key].keys():
                addresses[key]['main'] = False
        account = request.user.account
        fields = ['name', 'address1', 'address2', 'zip_code',
                  'city', 'state', 'main']
        for i in account.shippinginfo_set.values():
            info = ShippingInfo.objects.get(id=i['id'])
            for field in fields:
                setattr(info, field, addresses[str(i['id'])][field])
            info.save()
        account.main_address = add_id
        account.save()
        return HttpResponseRedirect(self.success_url)


class DeleteAddress(UserPassesTestMixin, DeleteView):
    """Delete an address."""

    permission_required = ''
    model = ShippingInfo
    success_url = reverse_lazy('account')
    template_name = 'del_add.html'

    def test_func(self):
        """Validate access."""
        return self.request.user.access.has_address_delete

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(DeleteAddress, self).get_context_data(**kwargs)
        set_basic_context(context, 'account')
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
        set_basic_context(context, 'account')
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
            account.pic.delete()
            account.pic = data[1]['pic']
        if 'about' in data[0].keys():
            account.about = data[0]['about']
        if 'group' in data[0].keys():
            account.group = data[0]['group']
        if 'newsletter' in data[0].keys():
            account.newsletter = True
        else:
            account.newsletter = False
        numbers = ['0', '1', '2', '3', '4', '5',
                   '6', '7', '8', '9', '(', ')', '-']
        if 'home_number' in data[0].keys():
            number = data[0]['home_number']
            if number:
                if all(element in numbers for element in number):
                    if len(number) <= 14:
                        account.home_number = number
        if 'cell_number' in data[0].keys():
            number = data[0]['cell_number']
            if all(element in numbers for element in number):
                if len(number) <= 14:
                    account.cell_number = number
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
        set_basic_context(context, 'register')
        return context


class CustomLogView(LoginView):
    """Custom login view."""

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(LoginView, self).get_context_data(**kwargs)
        set_basic_context(context, 'login')
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
        set_basic_context(context, 'login')
        return context

    def form_valid(self, form):
        """Creating shipping model and update user account."""
        user = User.objects.get(username=self.object.user.username)
        account = form.save(commit=False)
        account.birth_day = validate_bday(form.data['birth_date_month'] + ' ' +
                                          form.data['birth_date_day'] + ' ' +
                                          form.data['birth_date_year'])
        if account.registration_complete:
            return HttpResponseRedirect(self.get_success_url())
        account.birthday_set = True
        account.save()
        event = {}
        event['name'] = account.first_name + account.last_name
        event['email'] = user.email
        birthday = account.birth_day.split('-')
        event['month'] = birthday[1]
        event['day'] = birthday[2]
        add_birthday(event)
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
        set_basic_context(context, 'gallery')
        context['tab'] = title
        context['gallery'] = title
        for file in context['galleries']:
            if file['name'].title() == title:
                folder = file['id']
        context['photos'] = drive_files(folder)
        for photo in context['photos']:
            photo['name'] = photo['name'].split('.')[0]
        return context


class OrderView(UpdateView):
    """Display the details of an order."""

    template_name = 'order.html'
    model = Order
    form_class = OrderUpdateForm
    success_url = reverse_lazy('orders')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(OrderView, self).get_context_data(**kwargs)
        title = 'Order #' + str(context['object'].id)
        if self.request.user.is_staff:
            context['staff'] = True
        context['title'] = title
        if context['object'].ship_to:
            context['address'] = context['object'].ship_to
        content = unpack(context['object'].order_content)
        context['prods'] = []
        context['servs'] = []
        for item in content:
            if item['type'] == 'prod':
                context['prods'].append(item)
        context['item_fields'] = ['quantity', 'color', 'length', 'diameter',
                                  'extras', 'files', 'description']
        set_basic_context(context, 'order')
        return context


class OrdersView(ListView):
    """Display the details of an order."""

    template_name = 'orders.html'
    model = Order

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(OrdersView, self).get_context_data(**kwargs)
        context['order_list'] = (context['order_list'].filter(paid=True)
                                                      .filter(complete=False)
                                                      .order_by('id'))
        set_basic_context(context, 'order')
        return context


class CommentView(UpdateView):
    """Comment on a client."""

    template_name = 'comment.html'
    model = Account
    success_url = reverse_lazy('users')
    fields = ['comments']

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(CommentView, self).get_context_data(**kwargs)
        set_basic_context(context, 'users')
        return context


class UsersView(ListView):
    """Display the details of an order."""

    template_name = 'users.html'
    model = Account

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(UsersView, self).get_context_data(**kwargs)
        context['account_list'] = (context['account_list']
                                   .filter(registration_complete=True)
                                   .order_by('id'))
        context['email_list'] = (context['account_list']
                                 .filter(newsletter=True)
                                 .order_by('id'))
        guest = User.objects.get(username='Guest')
        mailing = guest.account.mailing_list
        if mailing:
            mailing = mailing.split(', ')
            for email in mailing:
                for user in context['email_list']:
                    if email == user.user.email:
                        mailing.remove(email)
            context['unreg_email_list'] = mailing
            new_mailing = ''.join(mailing)
            guest.account.mailing_list = new_mailing
            guest.account.save()
        else:
            context['unreg_email_list'] = ''
        set_basic_context(context, 'users')
        return context


class ContactView(FormView):
    """Form to contact the shop."""

    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ContactView, self).get_context_data(**kwargs)
        context['api'] = os.environ.get('GOOGLE_API_KEY')
        set_basic_context(context, 'contact')
        return context

    def post(self, request, *args, **kwargs):
        """Send email with conact info."""
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            contact = EmailMessage(subject, message, from_email,
                                   ['rvfmsite@gmail.com'])
            contact.send(fail_silently=True)
            return HttpResponseRedirect(self.success_url)


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
    day = date[1].split(',')[0]
    month = date[0]
    year = date[2]
    if len(year) != 4:
        return
    if len(day) > 2:
        return
    if len(day) == 1:
        day = '0' + day
    if month not in MONTHS:
        return
    month = MONTHS[month]
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


def unpack(packed_list, unpack_as=None):
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
        elif not unpack_as:
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


def set_basic_context(context, page):
    """Helper function to set the basics per page."""
    context['cart_count'] = cart_count(context['view'].request)
    context['nbar'] = page
    context['galleries'] = get_galleries()
    return context
