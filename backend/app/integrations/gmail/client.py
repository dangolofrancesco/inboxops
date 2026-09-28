from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os


def build_gmail_service(refresh_token: str):
    """Costruisce il client Gmail a partire dal refresh token salvato."""
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )
    # Rinnova automaticamente l'access token se scaduto
    credentials.refresh(Request())
    return build("gmail", "v1", credentials=credentials)


def fetch_recent_message_ids(service, max_results: int = 10) -> list[dict]:
    """Restituisce gli ultimi N message ID dalla inbox."""
    result = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        labelIds=["INBOX"],
    ).execute()
    return result.get("messages", [])


def fetch_message_metadata(service, message_id: str) -> dict:
    """Recupera sender, subject, snippet per un singolo messaggio."""
    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format="metadata",
        metadataHeaders=["From", "Subject", "Date"],
    ).execute()

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    return {
        "gmail_message_id": msg["id"],
        "gmail_thread_id": msg["threadId"],
        "sender": headers.get("From"),
        "subject": headers.get("Subject"),
        "snippet": msg.get("snippet"),
        "received_at": headers.get("Date"),
    }