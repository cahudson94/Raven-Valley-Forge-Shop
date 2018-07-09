"""."""
import os
import datetime
from oauth2client import tools, client
from oauth2client.file import Storage

import httplib2
from apiclient import discovery

HOME = os.path.expanduser('~')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APPLICATION_NAME = 'Web client 1'
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'RVFS/client_secrete.json')
ENV_CLIENT_SECRET = os.environ.get('GOOGLE_CREDS')
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/drive']

try:
    flags = tools.argparser.parse_args([])
except ImportError:
    flags = None

shop_hours = 'rsbvvpdq2vkmefr4690mi11afo@group.calendar.google.com'
birthdays = '0l6ami6ttn8ace17skuh3b4nkg@group.calendar.google.com'


def get_credentials():
    """
    Get valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = HOME
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'google.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        if ENV_CLIENT_SECRET:
            with open('new_secret_file.txt', 'w+') as new_secret_file:
                new_secret_file.write(ENV_CLIENT_SECRET)
            secret_path = os.path.join(BASE_DIR, 'new_secret_file.txt')
            credentials = Storage(secret_path).get()
        else:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store, flags)
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
            {'email': info['email']},
        ],
    }

    return (service.events()
                   .insert(calendarId=birthdays,
                           body=event).execute())


def check_time_slot(time):
    """Check if slot is open."""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    service = discovery.build('calendar', 'v3', http=http)

    year = time[0]
    month = time[1]
    day = time[2]
    hour = time[3]

    start = '{}-{}-{}T{}:00:00-07:00'.format(year, month, day, hour)
    end = '{}-{}-{}T{}:00:00-07:00'.format(year, month, day, hour + 1)

    body = {
        "timeMin": start,
        "timeMax": end,
        "timeZone": 'America/Los_Angeles',
        "items": [
            {
                'id': 'primary',
            }
        ]
    }

    busy = service.freebusy().query(body=body).execute()
    busy = busy['calendars']['primary']['busy']

    return busy


def set_appointment(time, info):
    """Update time slot on calendar and send invite."""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

    service = discovery.build('calendar', 'v3', http=http)

    year = time[0]
    month = time[1]
    if len(month) == 1:
        month = '0' + month
    day = time[2]
    if len(day) == 1:
        day = '0' + day
    hour = time[3]

    start = '{}-{}-{}T{}:00:00-07:00'.format(year, month, day, hour)
    end = '{}-{}-{}T{}:00:00-07:00'.format(year, month, day, hour + 1)

    event = service.events().list(calendarId=shop_hours,
                                  timeMin=start, timeMax=end, singleEvents=True).execute()
    # import pdb; pdb.set_trace()
    slot_id = event['items'][0]['id']
    event = service.events().get(calendarId=shop_hours,
                                 eventId=slot_id).execute()
    service.events().delete(calendarId=shop_hours,
                            eventId=event['id']).execute()
    event = {
        'summary': 'Shop Appointment',
        'start': {
            'dateTime': start,
        },
        'end': {
            'dateTime': end,
        },
        'attendees': [
            {'email': info['email']},
        ],
    }
    service.events().insert(calendarId='primary', body=event).execute()


def main(drive_file):
    """Show basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(
        q=("'%s' in parents" % drive_file),
        fields="nextPageToken, files(id, name, webContentLink, webViewLink)").execute()
    items = results.get('files', [])
    if not items:
        return('No files found.')
    else:
        files = []
        for item in items:
            files.append(item)
        return files


def download(file_id):
    """Download specified file."""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    image = service.files().get_media(fileId=file_id).execute()
    with open(os.path.join(BASE_DIR, 'new_image.jpg'), 'wb+') as file:
        file.write(image)
    return file.name

if __name__ == '__main__':
    main(os.sys.argv[1])
