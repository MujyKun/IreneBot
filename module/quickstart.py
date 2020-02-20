from __future__ import print_function
import pickle
import os.path
import requests
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']
link_download = 'https://drive.google.com/open?id='
link_addon = ''


def main(file_name):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    drive_service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = drive_service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        pass
        #print('Files:')
        #for item in items:
            #print(u'{0} ({1})'.format(item['name'], item['id']))

    #create a folder
    #uncomment this for first run
    """
    file_metadata1 = {
        'name': 'JiU',
        'mimeType': 'application/vnd.google-apps.folder'
        }
    file1 = drive_service.files().create(body=file_metadata1,fields='id').execute()
    print ('Folder ID: %s' %file1.get('id'))
    """

    #INPUT THE FOLDER ID UNDER the variable JiU AFTER RUNNING FOR THE FIRST TIME - the following code already goes to a certain folder, may need to be altered since folder won't be found
    


    #YOU CAN COMMENT THIS ALL OUT FOR THE FIRST RUN AND UNCOMMENT THE SECOND PART
    JiU = ''
    folder_id = JiU
    file_metadata = {
        'name': file_name,
        'parents' : [folder_id]
        }
    file_location = 'Photos/{}'.format(file_name)
    media = MediaFileUpload(file_location, mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
    print ('File ID: %s'% file.get('id'))
    link_addon = file.get('id')
    final_url = link_download + link_addon
    f = open("link.txt","w")
    f.write(final_url)
    f.close
    #YOU CAN COMMENT THIS ALL OUT FOR THE FIRST RUN AND UNCOMMENT THE SECOND PART




#Uncomment this for first run
"""
    file_metadata = {
        'name': file_name
        }
    file_location = 'Photos/{}'.format(file_name)
    media = MediaFileUpload(file_location, mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata,media_body=media,fields='id').execute()
    print ('File ID: %s'% file.get('id'))
    link_addon = file.get('id')
    final_url = link_download + link_addon
    f = open("link.txt","w")
    f.write(final_url)
    f.close
"""
#Uncomment this for first run