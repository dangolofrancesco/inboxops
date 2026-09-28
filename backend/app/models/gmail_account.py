import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class GmailAccount(Base):
    __tablename__ = "gmail_accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    google_account_email: Mapped[str] = mapped_column(String, nullable=False)
    # In V1 salviamo il refresh token in chiaro — nota di sicurezza nel codice
    # In produzione: cifrare con cryptography.fernet
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_history_id: Mapped[str | None] = mapped_column(String, nullable=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)