"""Acount model for RVFS app."""
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Account(models.Model):
    """An account for users of RVFS app."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pic = models.ImageField(blank=True, upload_to='profile_pics',
                            max_length=100)
    first_name = models.CharField(max_length=25, default='')
    last_name = models.CharField(max_length=25, default='')
    birth_day = models.DateField(auto_now_add=True)
    cart = models.TextField(default='', blank=True)
    cart_total = models.DecimalField(max_digits=15, decimal_places=2,
                                     default=0.0)
    saved_products = models.TextField(default='', blank=True)
    saved_services = models.TextField(default='', blank=True)
    comments = models.TextField(default='', blank=True)
    birthday_set = models.BooleanField(default=False)
    registration_complete = models.BooleanField(default=False)
    has_address_delete = models.BooleanField(default=False)
    main_address = models.IntegerField(null=True, blank=True)
    group = models.CharField(max_length=30, default='', blank=True)
    about = models.TextField(default='', blank=True)
    newsletter = models.BooleanField(default=False)
    mailing_list = models.TextField(default='', blank=True)
    home_number = models.CharField(max_length=14, default='(000)-000-0000')
    cell_number = models.CharField(max_length=14, blank=True)

    def __str__(self):
        """Print for admin."""
        return self.user.username


class ShippingInfo(models.Model):
    """Address model for accounts."""

    name = models.CharField("Location Name", max_length=50)
    address1 = models.CharField("Address line 1", max_length=250)
    address2 = models.CharField("Address line 2", max_length=250, default='')
    zip_code = models.CharField("ZIP / Postal code", max_length=12)
    city = models.CharField("City", max_length=25)
    state = models.CharField("State", max_length=25)
    resident = models.ForeignKey(Account, on_delete=models.CASCADE,
                                 blank=True, null=True)
    main = models.BooleanField(default=False)

    def __str__(self):
        """Print for admin."""
        return str(self.resident) + ', ' + str(self.name)


class Order(models.Model):
    """Order detail model."""

    buyer = models.ForeignKey(Account, on_delete=models.CASCADE,
                              blank=True, null=True)
    ship_to = models.ForeignKey(ShippingInfo, on_delete=models.CASCADE,
                                blank=True, null=True)
    recipient = models.CharField(max_length=40, default='')
    recipient_email = models.CharField(max_length=40, default='')
    tracking = models.CharField(max_length=35, default='')
    shipped = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    order_content = models.TextField()
    complete = models.BooleanField(default=False)

    def __str__(self):
        """Print for admin."""
        return 'Order Number %d' % self.id


class SlideShowImage(models.Model):
    """Slide image model."""

    image = models.ImageField(upload_to='slides')
    name = models.CharField(max_length=50)

    def __str__(self):
        """Print for admin."""
        return self.name


@receiver(post_save, sender=User)
def make_account_for_new_user(sender, **kwargs):
    """Reciever creates account for new users."""
    if kwargs['created']:
        new_account = Account(
            user=kwargs['instance']
        )
        new_account.save()
