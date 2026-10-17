import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

class GoogleWorkspaceService:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/documents',
                       'https://www.googleapis.com/auth/spreadsheets',
                       'https://www.googleapis.com/auth/presentations']

    def _get_service(self, api_name, version, key_path):
        creds = service_account.Credentials.from_service_account_file(
            os.getenv(key_path), scopes=self.scopes)
        return build(api_name, version, credentials=creds)

    def create_doc(self, title):
        service = self._get_service('docs', 'v1', 'GOOGLE_DOCS_API_KEY_PATH')
        doc = service.documents().create(body={'title': title}).execute()
        return doc.get('documentId')

    def create_sheet(self, title):
        service = self._get_service('sheets', 'v4', 'GOOGLE_SPREADSHEETS_API_KEY_PATH')
        spreadsheet = service.spreadsheets().create(body={'properties': {'title': title}}).execute()
        return spreadsheet.get('spreadsheetId')

    def create_slide(self, title):
        service = self._get_service('slides', 'v1', 'GOOGLE_SLIDES_API_KEY_PATH')
        presentation = service.presentations().create(body={'title': title}).execute()
        return presentation.get('presentationId')
