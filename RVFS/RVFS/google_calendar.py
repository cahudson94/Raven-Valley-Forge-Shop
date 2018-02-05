"""."""
import os
import datetime
from oauth2client import tools, client
from oauth2client.file import Storage

import httplib2
from apiclient import discovery

APPLICATION_NAME = 'Web client 1'
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = 'https://www.googleapis.com/auth/calendar'

try:
    flags = tools.argparser.parse_args([])
except ImportError:
    flags = None


def get_credentials():
    """
    Get valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def add_birthday(info):
    """."""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    service = discovery.build('calendar', 'v3', http=http)
    year = datetime.datetime.now().year
    event = {
        'summary': '{}\'s Birthday'.format(info['name']),
        'start': {
            'date': '{}-{}-{}'.format(str(year), str(info['month']), str(info['day'])),
        },
        'end': {
            'date': '{}-{}-{}'.format(str(year), str(info['month']), str(int(info['day']) + 1)),
        },
        'recurrence': [
            'RRULE:FREQ=YEARLY;'
        ],
        'attendees': [
            {'email': 'ravenmoorevalleyforge@gmail.com'},
            {'email': info['email']},
        ],
    }

    return (service.events()
                   .insert(calendarId='0l6ami6ttn8ace17skuh3b4nkg@group.calendar.google.com',
                           body=event).execute())


def get_calendar():
    """."""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    service = discovery.build('calendar', 'v3', http=http)
    calendar = service.calendarList().list().execute()

    return calendar

if __name__ == '__main__':
    get_credentials()
