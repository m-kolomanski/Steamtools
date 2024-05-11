import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64

class Mailer:
    def __init__(self, sender, boilerplate = None):
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        self.SENDER = sender
        self.SUBJECT = "New achievements for your games have been added"

        self.boilerplate = boilerplate

        if self.boilerplate == None:
            self.boilerplate = "This is an automatic message, please do not respond.\nNew achievements are available for games on your list:\n"

        creds = None
        if os.path.exists('token.json'):
            try:
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)

                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif not creds.valid:
                    flow = InstalledAppFlow.from_client_secrets_file('token.json', SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
                    creds = flow.run_local_server(port=0)

                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
            except:
                flow = InstalledAppFlow.from_client_secrets_file('token.json', SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
                creds = flow.run_local_server(port=0)

                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
        else:
            raise Exception ("In order to send emails, you need to configure gmail API access. Save your token in token.json file in main directory.")

        self.service = build('gmail', 'v1', credentials=creds)
        
    def sendMessage(self, to, message_list):
        message = self.createMessage(to, message_list)
        try:
            resp = self.service.users().messages().send(userId='me', body=message).execute()
            if resp['labelIds'][0] != "SENT":
                print(f"Failed to email {to}")
        except HttpError as error:
            print(f"An error occurred: {error}")

    def createMessage(self, to, message_list):
        message = MIMEText(self.boilerplate + '\n' + '\n'.join(message_list))
        message['to'] = to
        message['from'] = self.SENDER
        message['subject'] = self.SUBJECT
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw}