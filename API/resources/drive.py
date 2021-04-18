from __future__ import print_function
import pickle
import os.path
import io
# noinspection PyPackageRequirements
from googleapiclient.http import MediaIoBaseDownload
# noinspection PyPackageRequirements
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
# noinspection PyPackageRequirements
from google.auth.transport.requests import Request


def get_drive_connection():
    scopes = ['https://www.googleapis.com/auth/drive']
    cred = None
    if os.path.exists(f'token.pickle'):
        with open(f'token.pickle', 'rb') as token:
            try:
                cred = pickle.load(token)
            except Exception as e:
                print(e)
    # If there are no (valid) credentials available, let the user log in.
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            cred = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f'token.pickle', 'wb') as token:
            pickle.dump(cred, token)

    drive_service = build('drive', 'v3', credentials=cred)
    return drive_service


drive = get_drive_connection()


def get_file_type(file_id):
    """Get the file type of a drive file.
    ex: image.jpeg or media.mp4"""
    file_data = get_file_data(file_id)
    file_type = file_data.get('mimeType')
    if file_type:
        return file_type.replace('/', '.')
    return file_data.get('mimeType')


def get_file_data(file_id):
    """Get the file data of a drive file."""
    return drive.files().get(fileId=file_id).execute()


def download_media(file_id, file_location):
    media = drive.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, media)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print percentage of download
        print("Download %d%%." % int(status.progress() * 100))
    with open(file_location, 'wb') as f:
        fh.seek(0)  # go to start of stream
        f.write(fh.read())
    try:
        fh.close()
    except Exception as e:
        print(e, "--download")
