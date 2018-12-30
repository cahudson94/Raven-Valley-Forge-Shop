"""."""
import os
import datetime
from oauth2client import tools
from google.oauth2 import service_account
from googleapiclient.discovery import build

HOME = os.path.expanduser('~')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/admin.directory.group',
          'https://www.googleapis.com/auth/admin.directory.group.member',
          'https://www.googleapis.com/auth/admin.directory.user',
          ]

try:
    flags = tools.argparser.parse_args([])
except ImportError:
    flags = None

birthdays = '0l6ami6ttn8ace17skuh3b4nkg@group.calendar.google.com'
mailing_group = '01gf8i831vs9b7q'


def get_creds():
    """Open and return stored creds."""
    secret_path = os.path.join(BASE_DIR, 'RVFS/service_account.json')
    creds = service_account.Credentials.from_service_account_file(
        secret_path, scopes=SCOPES
    )
    creds.with_subject('muninn@ravenvfm.com')
    return creds


def add_birthday(info):
    """Add a client birthday to calendar."""
    creds = get_creds()

    service = build('calendar', 'v3', credentials=creds)
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

    service = build('admin', 'directory_v1', credentials=creds)
    mailing_list = set(mailing_list)
    import pdb; pdb.set_trace()
    old_members = (service.members().list(groupKey='01gf8i831vs9b7q')
                          .execute())
    if 'members' in old_members.keys():
        for member in old_members['members']:
            if member['email'] not in mailing_list:
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
    service = build('drive', 'v3', credentials=creds)
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
    service = build('drive', 'v3', credentials=creds)
    image = service.files().get_media(fileId=file_id).execute()
    with open(os.path.join(BASE_DIR, 'new_image.jpg'), 'wb+') as file:
        file.write(image)
    return file.name

if __name__ == '__main__':
    update_mailing_list(
        [' rvfm-700@rvfm-1537319214218.iam.gserviceaccount.com ',
         'Muninn@ravenvfm.com']
    )
