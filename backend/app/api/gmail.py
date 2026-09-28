from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.gmail_account import GmailAccount
from app.models.source_message import SourceMessage
from app.integrations.gmail.client import (
    build_gmail_service,
    fetch_recent_message_ids,
    fetch_message_metadata,
)

router = APIRouter(prefix="/gmail", tags=["gmail"])


@router.get("/status")
def gmail_status(db: Session = Depends(get_db)):
    """Controlla se c'è un account Gmail connesso."""
    account = db.query(GmailAccount).first()
    if not account:
        return {"connected": False}
    return {
        "connected": True,
        "email": account.google_account_email,
        "last_sync_at": account.last_sync_at,
    }


@router.post("/sync")
def sync_gmail(db: Session = Depends(get_db)):
    """Fetcha le ultime 10 email e salva i metadati nel DB."""
    account = db.query(GmailAccount).first()
    if not account or not account.encrypted_refresh_token:
        raise HTTPException(status_code=400, detail="Nessun account Gmail connesso")

    service = build_gmail_service(account.encrypted_refresh_token)
    message_ids = fetch_recent_message_ids(service, max_results=10)

    saved = 0
    skipped = 0

    for msg_ref in message_ids:
        message_id = msg_ref["id"]

        # Idempotenza: salta se già salvato
        existing = db.query(SourceMessage).filter(
            SourceMessage.gmail_message_id == message_id
        ).first()
        if existing:
            skipped += 1
            continue

        metadata = fetch_message_metadata(service, message_id)

        message = SourceMessage(
            user_id=account.user_id,
            gmail_message_id=metadata["gmail_message_id"],
            gmail_thread_id=metadata["gmail_thread_id"],
            sender=metadata["sender"],
            subject=metadata["subject"],
            snippet=metadata["snippet"],
        )
        db.add(message)
        saved += 1

    account.last_sync_at = datetime.now(timezone.utc)
    db.commit()

    return {"saved": saved, "skipped": skipped, "total": len(message_ids)}