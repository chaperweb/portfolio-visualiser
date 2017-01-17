
from __future__ import print_function
import httplib2
import os

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials

CLIENT_SECRET_FILE = os.path.dirname(os.path.realpath(__file__))+'/client_id.json'
API_KEY='AIzaSyDj4jirLkmyIwe42rTpdkeqY7DlCoNsIAU'

def run():

    credentials = GoogleCredentials.from_stream(CLIENT_SECRET_FILE)
    service = build('sheets', 'v4', credentials=credentials, developerKey=API_KEY)

    spreadsheetId = '1h4qJYKxL7EhjIXh2tUghSdNAEQalc2fPwTSqHu6CrmY'
    rangeName = 'Taulukko1!A1:T'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s' % (row))


if __name__ == '__main__':
    run()

