import uuid
from datetime import datetime
from pydantic import BaseModel


class ApplicationResponse(BaseModel):
    id: uuid.UUID          # this is the entity id
    title: str
    current_state: str
    company: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}