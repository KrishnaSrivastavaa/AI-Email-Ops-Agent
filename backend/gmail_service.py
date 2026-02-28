import os
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from datetime import datetime, timedelta


from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SCOPES, GOOGLE_REDIRECT_URI
from database import get_db
from models import User, GmailAccount
from auth.jwt_auth import create_access_token, get_current_user


router = APIRouter()

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



@router.get("/auth/google/login")
def login():
    flow = create_flow()

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    return RedirectResponse(auth_url)


@router.get("/auth/google/callback")
def callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="No code")

    flow = create_flow()
    flow.fetch_token(code=code)

    credentials = flow.credentials

    oauth_service = build("oauth2", "v2", credentials=credentials)
    user_info = oauth_service.userinfo().get().execute()

    email = user_info.get("email")
    full_name = user_info.get("name", "Unknown")

     # Create or fetch user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(email=email, full_name=full_name)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if credentials.refresh_token:
        existing = db.query(GmailAccount).filter(
            GmailAccount.user_id == user.id
        ).first()

        if existing:
            existing.refresh_token = credentials.refresh_token
        else:
            gmail_account = GmailAccount(
                user_id=user.id,
                gmail_email=email,
                refresh_token=credentials.refresh_token,
            )
            db.add(gmail_account)

        db.commit()
    access_token = create_access_token(user.id)
    response = RedirectResponse(url="/emails")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,   # True in production (HTTPS)
        samesite="lax"
    )

    return response


@router.get("/emails")
def get_emails(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    gmail_account = db.query(GmailAccount).filter(
        GmailAccount.user_id == current_user.id
    ).first()

    if not gmail_account:
        raise HTTPException(status_code=400, detail="Gmail not connected")

    service = build_gmail_service(gmail_account.refresh_token)

    results = service.users().messages().list(
        userId="me",
        q="in:inbox category:primary",
        maxResults=5
    ).execute()

    messages = results.get("messages", [])
    full_messages = []

    for message in messages:
        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"   # important
        ).execute()

        full_messages.append(msg)

    return full_messages


def build_gmail_service(refresh_token):
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )

    creds.refresh(GoogleRequest())

    service = build("gmail", "v1", credentials=creds)
    return service