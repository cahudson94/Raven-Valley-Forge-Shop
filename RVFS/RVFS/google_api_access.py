"""."""
import os
import datetime
from oauth2client import tools, file, client
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

birthdays = '0l6ami6ttn8ace17skuh3b4nkg@group.calendar.google.com'
mailing_group = '01gf8i831vs9b7q'


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
                                   'token.json')

    store = file.Storage(credential_path)
    creds = store.get()
    if not creds or creds.invalid:
        with open('token.json', 'w+') as credentials:
            credentials.write(ENV_CLIENT_SECRET)
        secret_path = os.path.join(BASE_DIR, 'RVFS/token.json')
        creds = file.Storage(secret_path).get()
    return creds


def add_birthday(info):
    """Add a client birthday to calendar."""
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


def update_mailing_list(mailing_list):
    """Check and update mailing list."""
    creds = get_creds()
    http = creds.authorize(Http())

    service = build('admin', 'directory_v1', http=http)
    copy_list = mailing_list[:]
    old_members = (service.members().list(groupKey='01gf8i831vs9b7q')
                          .execute())
    if 'members' in old_members.keys():
        for member in old_members['members']:
            if member['email'] not in copy_list:
                service.members().delete(groupKey='01gf8i831vs9b7q',
                                         memberKey=member['id']).execute()
            else:
                mailing_list.remove(member['email'])
    for email in mailing_list:
        new_member = {
            "kind": "admin#directory#member",
            "email": email,
            "role": 'MEMBER',
            "type": 'EXTERNAL'
        }
        service.members().insert(groupKey='01gf8i831vs9b7q',
                                 body=new_member
                                 ).execute()
    return '<p class="nav-link staff-nav">List updated!</p>'


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


def add_creds():
    """Run to open oauth prompt for new creds."""
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('admin', 'directory_v1', http=creds.authorize(Http()))
    print('Getting the first 10 users in the domain')
    results = service.groups().list(customer='my_customer', maxResults=10,
                                    orderBy='email').execute()
    users = results.get('groups', [])

    if not users:
        print('No users in the domain.')
    else:
        print('Users:')
        for user in users:
            print(u'{0} ({1})'.format(user['primaryEmail'],
                                      user['name']['fullName']))


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
