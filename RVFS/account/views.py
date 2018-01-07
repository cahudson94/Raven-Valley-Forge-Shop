"""."""
from django.shortcuts import render
import random
from products.models import SliderImages
from registration.backends.hmac.views import RegistrationView
from account.forms import CustomRegForm
from django.contrib.auth.models import User


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


def account(request):
    """."""
    context = {'Hello': "Hello, world. This is the account page."}
    return render(request, 'account/account.html', context)


class CustomRegView(RegistrationView):
    """."""

    form_class = CustomRegForm
    model = User

    def get_context_data(self, **kwargs):
        """."""
        context = super(RegistrationView, self).get_context_data(**kwargs)
        # import pdb; pdb.set_trace()
        # info = ['first_name', 'last_name', 'birth_date']
        # context['info_fields'] = [context['form'].fields[i] for i in info]
        context['nbar'] = 'register'
        return context
