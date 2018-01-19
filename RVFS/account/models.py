"""Acount model for RVFS app."""
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Account(models.Model):
    """An account for users of RVFS app."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pic = models.ImageField(blank=True, upload_to='profile_pics', max_length=100)
    first_name = models.CharField(max_length=25, default='')
    last_name = models.CharField(max_length=25, default='')
    birth_day = models.DateField(auto_now_add=True)
    cart = []
    cart_total = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    orders = []
    purchase_history = []
    service_history = []
    saved_products = []
    saved_services = []
    comments = models.TextField(default='')
    registration_complete = models.BooleanField(default=False)

    def __str__(self):
        """Print for admin."""
        return self.user.username


class ShippingInfo(models.Model):
    """Address model for accounts."""

    address1 = models.CharField("Address line 1", max_length=250)
    address2 = models.CharField("Address line 2", max_length=250)
    zip_code = models.CharField("ZIP / Postal code", max_length=12)
    city = models.CharField("City", max_length=25)
    state = models.CharField("State", max_length=25)
    resident = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='addresses', blank=True, null=True)

    def __str__(self):
        """Print for admin."""
        return str(self.resident)


# @receiver(post_save, sender=Account)
# def set_birthday_to_calander(sender, **kwargs):
#     """Add user birthday to calander."""
#     if kwargs['created']:
#         new_account = Account(
#             user=kwargs['instance']
#         )
#         new_account.save()


@receiver(post_save, sender=User)
def make_account_for_new_user(sender, **kwargs):
    """Reciever creates account for new users."""
    if kwargs['created']:
        new_account = Account(
            user=kwargs['instance']
        )
        new_account.save()
