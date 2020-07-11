from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from module import logger as log


class Drive:
    """
    Google Drive API, Any methods for uploading were moved to an external program.
    WARNING: If deciding to use this directly from a discord bot, this class is not ASYNC and could cause a few
    seconds of blocking.
    This is kept here for easier access to uploading images directly from discord instead of connecting to the server.
    The server has an external program that does the necessary google drive functions for the GroupMembers category.
    """
    @staticmethod
    def get_drive_connection():
        SCOPES = ['https://www.googleapis.com/auth/drive']
        link_download = 'https://drive.google.com/open?id='
        link_addon = ''
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle') or os.path.exists('../token.pickle'):
            try:
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            except:
                with open('../token.pickle', 'rb') as token:
                    creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                except:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        '../credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        drive_service = build('drive', 'v3', credentials=creds)
        return drive_service

    @staticmethod
    async def get_ids(folder_id):
        # This function was changed to somewhat support recursion in the case that I figure out how to properly
        # get back requests with the next page token and not get a invalid parameter error
        drive_service = Drive.get_drive_connection()

        async def response(page_fields='nextPageToken, files(id, name)', amount=1000, page_token=None):
            try:
                if page_token is None:
                    drive_response = drive_service.files().list(q=f"'{folder_id}' in parents",
                                                          spaces='',
                                                          fields=page_fields,
                                                          pageSize=amount).execute()
                    return drive_response
                else:
                    # This should get requests from next page token
                    return False
            except Exception as e:
                log.console(e)
                return False

        id_list = []

        async def next_page(page_token=None):
            response_msg = await response(page_token)
            # next_page_token = response_msg.get('nextPageToken')
            if response_msg:
                for file in response_msg.get('files', []):
                    id_list.append(file.get('id'))
            # if next_page_token is not None:
                # next_page_start = await next_page(next_page_token)
            # return False

        await next_page()
        return id_list
