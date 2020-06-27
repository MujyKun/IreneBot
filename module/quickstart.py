from __future__ import print_function
import pickle
import os.path
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from module import logger as log
from Utility import DBconn, c, fetch_one, fetch_all


class Drive:
    def __init__(self):
    	"""Note this is the google framework and is not ASYNC. A wrapper can be used that makes it async."""
        pass

    @staticmethod
    def checker():
        c.execute("SELECT COUNT(*) FROM archive.ArchivedChannels")
        check = fetch_one()
        if check > 0:
            c.execute("SELECT id, filename, filetype, folderid FROM archive.ArchivedChannels")
            posts = fetch_all()
            for post in posts:
                ID = post[0]
                FileName = post[1]
                FileType = post[2]
                FolderID = post[3]
                Drive.upload_to_drive(ID, FolderID, FileName, FileType)

    @staticmethod
    def upload_to_drive(ID, folder_id, file_name, file_type):
        try:
            drive_service = Drive.get_drive_connection()
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
                }
            if len(file_type) == 4:
                file_type = file_type[1:3]
            # print(file_name)
                file_location = f'Photos/{file_name}'
                media = MediaFileUpload(file_location)
                file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            c.execute("DELETE FROM archive.ArchivedChannels WHERE ID = %s", (ID,))
            DBconn.commit()
            # print ('File ID: %s'% file.get('id'))
            # link_addon = file.get('id')
        except Exception as e:
            log.console(e)

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
