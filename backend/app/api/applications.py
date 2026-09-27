import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.entity import Entity
from app.models.application import Application
from app.schemas.application import ApplicationResponse

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationResponse])
def list_applications(db: Session = Depends(get_db)):
    """Return all applications with their entity data."""
    entities = (
        db.query(Entity)
        .filter(Entity.entity_type == "APPLICATION")
        .options(joinedload(Entity.application))  # load application in the same query
        .order_by(Entity.created_at.desc())
        .all()
    )
    return [
        ApplicationResponse(
            id=e.id,
            title=e.title,
            current_state=e.current_state,
            company=e.application.company,
            role=e.application.role,
            created_at=e.created_at,
        )
        for e in entities
    ]


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: uuid.UUID, db: Session = Depends(get_db)):
    """Return one application by entity ID."""
    entity = (
        db.query(Entity)
        .filter(Entity.id == application_id, Entity.entity_type == "APPLICATION")
        .options(joinedload(Entity.application))
        .first()
    )
    if not entity:
        raise HTTPException(status_code=404, detail="Application not found")
    return ApplicationResponse(
        id=entity.id,
        title=entity.title,
        current_state=entity.current_state,
        company=entity.application.company,
        role=entity.application.role,
        created_at=entity.created_at,
    )