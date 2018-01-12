"""."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from products.models import SliderImages
from registration.backends.hmac.views import RegistrationView
from registration.forms import RegistrationForm
from account.models import Account, ShippingInfo
from account.forms import InfoRegForm
from django.views.generic import ListView, UpdateView
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import login as auth_login
import random


def home(request):
    """."""
    pics = [i for i in SliderImages.objects.all()]
    count = min(5, len(pics))
    rand_pics = random.sample(pics, count)
    context = {'Hello': "Hello, world. This is the home page.",
               'random_pics': rand_pics,
               'nbar': 'home'}
    return render(request, 'rvfsite/home.html', context)


def about(request):
    """."""
    context = {'Hello': "Hello, world. This is the about page.",
               'nbar': 'about'}
    return render(request, 'rvfsite/about.html', context)


class AccountView(LoginRequiredMixin, ListView):
    """Custom geistration view."""

    template_name = 'account.html'
    model = Account

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(ListView, self).get_context_data(**kwargs)
        context['account'] = context['view'].request.user.account
        context['addresses'] = context['view'].request.user.addresses.get()
        context['nbar'] = 'account'
        return context


class CustomReg(RegistrationView):
    """Custom regeistration view."""

    form_class = RegistrationForm
    model = User

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(RegistrationView, self).get_context_data(**kwargs)
        context['nbar'] = 'register'
        return context


class CustomLog(LoginView):
    """Custom login view."""

    def get_context_data(self, **kwargs):
        """Add context for active page."""
        context = super(LoginView, self).get_context_data(**kwargs)
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
    """."""

    template_name = 'info-form.html'
    form_class = InfoRegForm
    success_url = '/login'
    model = Account

    def form_valid(self, form):
        """Creating shipping model and update user account."""
        user = User.objects.get(username=form.cleaned_data['user_name'])
        account = Account.objects.get(user=user)
        account.birth_day = form.cleaned_data['birth_date']
        account.registration_complete = True
        account.first_name = form.cleaned_data['first_name']
        account.last_name = form.cleaned_data['last_name']
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
        account.save()
        new_info.save()
        return HttpResponseRedirect(self.get_success_url())
