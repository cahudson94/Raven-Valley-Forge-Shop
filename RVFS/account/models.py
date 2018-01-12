"""Acount model for RVFS app."""
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Account(models.Model):
    """An account for users of RVFS app."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pic = models.ImageField(upload_to='profile_pics')
    first_name = models.CharField(max_length=25, default='')
    last_name = models.CharField(max_length=25, default='')
    birth_day = models.DateTimeField(auto_now_add=True)
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


@receiver(post_save, sender=User)
def make_account_for_new_user(sender, **kwargs):
    """Reciever creates account for new users."""
    if kwargs['created']:
        new_account = Account(
            user=kwargs['instance']
        )
        new_account.save()
