import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.db.session import get_db
from app.integrations.gmail.oauth import build_flow
from app.models.user import User
from app.models.gmail_account import GmailAccount

router = APIRouter(prefix="/auth", tags=["auth"])

# Stato temporaneo in memoria per il flow OAuth
# In produzione: usare Redis o sessioni firmate
_oauth_state: dict = {}


@router.get("/google")
def google_login():
    flow = build_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )
    # Salva state E code_verifier
    _oauth_state["state"] = state
    _oauth_state["code_verifier"] = flow.code_verifier  # aggiungi questa riga
    return RedirectResponse(auth_url)


@router.get("/google/callback")
def google_callback(
    db: Session = Depends(get_db),
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):



    if error:
        return {"error": error}
    if not code:
        return {"error": "no code received"}

    """Step 2: Google reindirizza qui con il code. Lo scambiamo con i token."""
    flow = build_flow()
    flow.fetch_token(
        code=code,
        code_verifier=_oauth_state.get("code_verifier"),  # aggiungi questa riga
    )
    credentials = flow.credentials

    # Recupera il profilo utente con l'access token
    service = build("oauth2", "v2", credentials=credentials)
    user_info = service.userinfo().get().execute()
    email = user_info["email"]

    # Crea o recupera l'utente nel DB
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
        db.flush()

    # Salva o aggiorna l'account Gmail
    gmail_account = db.query(GmailAccount).filter(
        GmailAccount.user_id == user.id
    ).first()

    if not gmail_account:
        gmail_account = GmailAccount(
            user_id=user.id,
            google_account_email=email,
            encrypted_refresh_token=credentials.refresh_token,
        )
        db.add(gmail_account)
    else:
        if credentials.refresh_token:
            gmail_account.encrypted_refresh_token = credentials.refresh_token

    db.commit()
    return {"message": f"Connesso come {email}", "user_id": str(user.id)}