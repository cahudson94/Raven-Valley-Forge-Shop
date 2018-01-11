"""."""
from django import forms
from account.models import Account
import datetime

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

YEARS = [x for x in range(current_year - 117, current_year - 17)]
YEARS = YEARS[::-1]


class InfoRegForm(forms.ModelForm):
    """."""

    user_name = forms.CharField(max_length=35)
    # first_name = forms.CharField(max_length=25)
    # last_name = forms.CharField(max_length=25)
    birth_date = forms.CharField(widget=forms.SelectDateWidget(years=YEARS))
    street = forms.CharField(max_length=90, label='Address Line 1')
    adr_extra = forms.CharField(required=False, max_length=90, label='Address Line 2')
    zip_code = forms.CharField(max_length=10, label='Zip Code')
    city = forms.CharField(max_length=25, label='City')
    state = forms.ChoiceField(required=True, choices=STATES, label='State')

    class Meta():
        """."""

        model = Account
        fields = ['first_name', 'last_name']
