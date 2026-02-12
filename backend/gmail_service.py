import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SCOPES, GOOGLE_REDIRECT_URI


app = FastAPI()

# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# REDIRECT_URI = "http://localhost:8000/callback"


def create_flow():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    return flow


@app.get("/login")
def login():
    flow = create_flow()

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    return RedirectResponse(auth_url)


@app.get("/auth/google/callback")
def callback(request: Request):
    code = request.query_params.get("code")

    if not code:
        return {"error": "No code received"}

    flow = create_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials

    service = build("gmail", "v1", credentials=credentials)
    results = (
        service.users().messages().list(userId="me", q="in:inbox category:primary", maxResults=10).execute()
    )
    messages = results.get("messages", [])
    res = []
    for message in messages:
        msg = (
            service.users().messages().get(userId="me", id=message["id"], format="full").execute()
        )
        res.append({message["id"]: msg})
    return {
        "message": "Success",
        "labels": res

    }
