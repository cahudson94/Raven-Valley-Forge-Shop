"""."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from registration.backends.hmac.views import RegistrationView
from registration.forms import RegistrationForm
from account.models import Account, ShippingInfo
from account.forms import InfoRegForm
from django.views.generic import ListView, UpdateView, TemplateView
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login
from RVFS.google_drive import main as drive_files
import random


class HomeView(TemplateView):
    """Home View."""

    template_name = 'rvfsite/home.html'

    def get_context_data(self, **kwargs):
        """."""
        slide_files = drive_files('17fqQwUu1dGPOUBirLDo2O0tBg_TUXMlZ')
        rand_pics = random.sample(slide_files, min(5, len(slide_files)))
        context = super(TemplateView, self).get_context_data(**kwargs)
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
        context['addresses'] = context['view'].request.user.addresses.get()
        context['galleries'] = get_galleries()
        context['nbar'] = 'account'
        return context


class CustomRegView(RegistrationView):
    """Custom regeistration view."""

    form_class = RegistrationForm
    model = User

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(RegistrationView, self).get_context_data(**kwargs)
        context['galleries'] = get_galleries()
        context['nbar'] = 'register'
        return context


class CustomLogView(LoginView):
    """Custom login view."""

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(LoginView, self).get_context_data(**kwargs)
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
        context['galleries'] = get_galleries()
        context['nbar'] = 'login'
        return context

    def form_valid(self, form):
        """Creating shipping model and update user account."""
        user = User.objects.get(username=form.cleaned_data['user_name'])
        account = Account.objects.get(user=user)
        if account.registration_complete:
            return HttpResponseRedirect(self.get_success_url())
        account.birth_day = form.cleaned_data['birth_date']
        account.first_name = form.cleaned_data['first_name']
        account.last_name = form.cleaned_data['last_name']
        account.pic = form.cleaned_data['pic']
        account.birthday_set = True
        account.save()
        new_info = ShippingInfo()
        new_info.address1 = form.cleaned_data['street']
        if form.cleaned_data['adr_extra']:
            new_info.address2 = form.cleaned_data['adr_extra']
        new_info.zip_code = form.cleaned_data['zip_code']
        new_info.city = form.cleaned_data['city']
        new_info.state = form.cleaned_data['state']
        new_info.save()
        new_info.resident = user
        account.registration_complete = True
        account.save()
        new_info.save()
        auth_login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())


class GalleryView(TemplateView):
    """."""

    template_name = 'gallery.html'

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(GalleryView, self).get_context_data(**kwargs)
        title = context['slug'].replace('_', ' ').title()
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
    """."""
    files = drive_files('18HHO951sd6wkp_tCREzHQimX8ntwVycq')
    for file in files:
        file['url'] = file['name'].lower().replace(' ', '_')
    return files
