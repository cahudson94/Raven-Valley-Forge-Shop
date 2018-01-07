"""."""
from registration.forms import RegistrationForm
from django import forms
import datetime

STATES = ([
    ('ALABAMA', 'AL'),
    ('ALASKA', 'AK'),
    ('ARIZONA', 'AZ'),
    ('ARKANSAS', 'AR'),
    ('CALIFORNIA', 'CA'),
    ('COLORADO', 'CO'),
    ('CONNECTICUT', 'CT'),
    ('DELAWARE', 'DE'),
    ('FLORIDA', 'FL'),
    ('GEORGIA', 'GA'),
    ('HAWAII', 'HI'),
    ('IDAHO', 'ID'),
    ('ILLINOIS', 'IL'),
    ('INDIANA', 'IN'),
    ('IOWA', 'IA'),
    ('KANSAS', 'KS'),
    ('KENTUCKY', 'KY'),
    ('LOUISIANA', 'LA'),
    ('MAINE', 'ME'),
    ('MARYLAND', 'MD'),
    ('MASSACHUSETTS', 'MA'),
    ('MICHIGAN', 'MI'),
    ('MINNESOTA', 'MN'),
    ('MISSISSIPPI', 'MS'),
    ('MISSOURI', 'MO'),
    ('MONTANA', 'MT'),
    ('NEBRASKA', 'NE'),
    ('NEVADA', 'NV'),
    ('NEW HAMPSHIRE', 'NH'),
    ('NEW JERSEY', 'NJ'),
    ('NEW MEXICO', 'NM'),
    ('NEW YORK', 'NY'),
    ('NORTH CAROLINA', 'NC'),
    ('NORTH DAKOTA', 'ND'),
    ('OHIO', 'OH'),
    ('OKLAHOMA', 'OK'),
    ('OREGON', 'OR'),
    ('PENNSYLVANIA', 'PA'),
    ('RHODE ISLAND', 'RI'),
    ('SOUTH CAROLINA', 'SC'),
    ('SOUTH DAKOTA', 'SD'),
    ('TENNESSEE', 'TN'),
    ('TEXAS', 'TX'),
    ('UTAH', 'UT'),
    ('VERMONT', 'VT'),
    ('VIRGINIA', 'VA'),
    ('WASHINGTON', 'WA'),
    ('WEST VIRGINIA', 'WV'),
    ('WISCONSIN', 'WI'),
    ('WYOMING', 'WY'),
])

current_year = datetime.datetime.now().year

YEARS = [x for x in range(current_year - 117, current_year - 17)]
YEARS = YEARS[::-1]


class CustomRegForm(RegistrationForm):
    """."""

    first_name = forms.CharField(max_length=25)
    last_name = forms.CharField(max_length=25)
    birth_date = forms.CharField(widget=forms.SelectDateWidget(years=YEARS))
    street = forms.CharField(max_length=90, label='Address Line 1')
    adr_extra = forms.CharField(required=False, max_length=90, label='Address Line 2')
    zip_code = forms.CharField(max_length=10, label='Zip Code')
    city = forms.CharField(max_length=25, label='City')
    state = forms.ChoiceField(required=True, choices=STATES, label='State')
