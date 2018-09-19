"""."""
import os
import datetime
from oauth2client import tools, file
from googleapiclient.discovery import build
from httplib2 import Http

HOME = os.path.expanduser('~')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENV_CLIENT_SECRET = os.environ.get('NEW_GOOGLE_CREDS')
SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/admin.directory.group',
          'https://www.googleapis.com/auth/admin.directory.group.member',
          ]

try:
    flags = tools.argparser.parse_args([])
except ImportError:
    flags = None

shop_hours = 'rsbvvpdq2vkmefr4690mi11afo@group.calendar.google.com'
birthdays = '0l6ami6ttn8ace17skuh3b4nkg@group.calendar.google.com'


def get_creds():
    """
    Get valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = HOME
    credential_dir = os.path.join(home_dir, '.creds')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'google.json')

    store = file.Storage(credential_path)
    creds = store.get()
    if not creds or creds.invalid:
        with open('credentials.json', 'w+') as credentials:
            credentials.write(ENV_CLIENT_SECRET)
        secret_path = os.path.join(BASE_DIR, 'RVFS/credentials.json')
        creds = file.Storage(secret_path).get()
    return creds


def add_birthday(info):
    """."""
    creds = get_creds()
    http = creds.authorize(Http())

    service = build('calendar', 'v3', http=http)
    year = datetime.datetime.now().year
    event = {
        'summary': '{}\'s Birthday'.format(info['name']),
        'start': {
            'date': '{}-{}-{}'.format(str(year),
                                      str(info['month']),
                                      str(info['day'])),
        },
        'end': {
            'date': '{}-{}-{}'.format(str(year),
                                      str(info['month']),
                                      str(int(info['day']) + 1)),
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
    creds = get_creds()
    http = creds.authorize(Http())

    service = build('calendar', 'v3', http=http)

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
    creds = get_creds()
    http = creds.authorize(Http())

    service = build('calendar', 'v3', http=http)

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
                                  timeMin=start, timeMax=end,
                                  singleEvents=True).execute()
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
    creds = get_creds()
    http = creds.authorize(Http())
    service = build('drive', 'v3', http=http)
    results = service.files().list(
        q=("'%s' in parents" % drive_file),
        fields="nextPageToken, files(id, name, \
webContentLink, webViewLink, properties, description)").execute()
    items = results.get('files', [])
    if items:
        files = []
        for item in items:
            files.append(item)
        return files


def download(file_id):
    """Download specified file."""
    creds = get_creds()
    http = creds.authorize(Http())
    service = build('drive', 'v3', http=http)
    image = service.files().get_media(fileId=file_id).execute()
    with open(os.path.join(BASE_DIR, 'new_image.jpg'), 'wb+') as file:
        file.write(image)
    return file.name

if __name__ == '__main__':
    main(os.sys.argv[1])
