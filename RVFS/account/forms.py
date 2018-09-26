"""."""
from django import forms
from account.models import Account, ShippingInfo, Order
import datetime

MONTHS = {
    'Jan.': 'Jan.',
    'Feb.': 'Feb.',
    'Mar.': 'Mar.',
    'Apr.': 'Apr.',
    'May': 'May',
    'Jun.': 'Jun.',
    'Jul.': 'Jul.',
    'Aug.': 'Aug.',
    'Sep.': 'Sep.',
    'Oct.': 'Oct.',
    'Nov.': 'Nov.',
    'Dec.': 'Dec.',
}

STATES = ([
    ('Alabama', 'AL'),
    ('Alaska', 'AK'),
    ('Arizona', 'AZ'),
    ('Arkansas', 'AR'),
    ('California', 'CA'),
    ('Colorado', 'CO'),
    ('Connecticut', 'CT'),
    ('Delaware', 'DE'),
    ('Florida', 'FL'),
    ('Georgia', 'GA'),
    ('Hawaii', 'HI'),
    ('Idaho', 'ID'),
    ('Illinois', 'IL'),
    ('Indiana', 'IN'),
    ('Iowa', 'IA'),
    ('Kansas', 'KS'),
    ('Kentucky', 'KY'),
    ('Louisiana', 'LA'),
    ('Maine', 'ME'),
    ('Maryland', 'MD'),
    ('Massachusetts', 'MA'),
    ('Michigan', 'MI'),
    ('Minnesota', 'MN'),
    ('Mississippi', 'MS'),
    ('Missouri', 'MO'),
    ('Montana', 'MT'),
    ('Nebraska', 'NE'),
    ('Nevada', 'NV'),
    ('New Hampshire', 'NH'),
    ('New Jersey', 'NJ'),
    ('New Mexico', 'NM'),
    ('New York', 'NY'),
    ('North Carolina', 'NC'),
    ('North Dakota', 'ND'),
    ('Ohio', 'OH'),
    ('Oklahoma', 'OK'),
    ('Oregon', 'OR'),
    ('Pennsylvania', 'PA'),
    ('Rhode Island', 'RI'),
    ('South Carolina', 'SC'),
    ('South Dakota', 'SD'),
    ('Tennessee', 'TN'),
    ('Texas', 'TX'),
    ('Utah', 'UT'),
    ('Vermont', 'VT'),
    ('Virginia', 'VA'),
    ('Washington', 'WA'),
    ('West Virginia', 'WV'),
    ('Wisconsin', 'WI'),
    ('Wyoming', 'WY')]
)

current_year = datetime.datetime.now().year

YEARS = [x for x in range(current_year - 100, current_year - 17)]
YEARS = YEARS[::-1]


class InfoRegForm(forms.ModelForm):
    """Extra registration info form."""

    birth_date = forms.CharField(widget=forms.SelectDateWidget(years=YEARS,
                                                               months=MONTHS))
    location_name = forms.CharField(max_length=35,
                                    label='Name for this Address')
    street = forms.CharField(max_length=90, label='Address Line 1')
    adr_extra = forms.CharField(required=False, max_length=90,
                                label='Address Line 2 (not required)')
    zip_code = forms.CharField(max_length=10, label='Zip Code')
    city = forms.CharField(max_length=25, label='City')
    state = forms.ChoiceField(required=True, choices=STATES, label='State')
    home_phone = forms.CharField(required=True, label="Home phone")
    cell_phone = forms.CharField(required=False,
                                 label="Cell phone (not required)")

    class Meta():
        """."""

        model = Account
        fields = ['first_name', 'last_name', 'pic']


class AddAddressForm(forms.ModelForm):
    """Add extra addresses form."""

    state = forms.ChoiceField(required=True, choices=STATES, label='State')
    address2 = forms.CharField(required=False, max_length=90,
                               label='Address Line 2')

    class Meta():
        """."""

        model = ShippingInfo
        exclude = ['resident', 'address2', 'state']


class OrderUpdateForm(forms.ModelForm):
    """Update orders with shipping or changes."""

    tracking = forms.CharField(required=False)
    appointment = forms.CharField(required=False)

    class Meta():
        """."""

        model = Order
        exclude = ['buyer', 'ship_to', 'order_content', 'payed']


class ContactForm(forms.Form):
    """Form to contact shop."""

    subject = forms.CharField(required=True, label="Your name:")
    from_email = forms.EmailField(required=True, label="Your email:")
    message = forms.CharField(
        required=True,
        widget=forms.Textarea,
        label="What can we help you with?"
    )
