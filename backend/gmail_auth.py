import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SCOPES, GOOGLE_REDIRECT_URI

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        code = params.get("code", [None])[0]

        print("Authorization code:", code)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"You can close this tab now.")



def main():
    flow = Flow.from_client_config(
        {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }, scopes=SCOPES
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    print("Go to this URL:", authorization_url)

    code = input("Enter the code from browser: ")

    flow.fetch_token(code=code)

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=flow.credentials)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
         print("No labels found.")
        return
        print("Labels:")
        for label in labels:
            print(label["name"])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()