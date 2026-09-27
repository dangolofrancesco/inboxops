"""Run once to insert sample data for development."""
from app.db.session import SessionLocal
from app.models.user import User
from app.models.entity import Entity
from app.models.application import Application


def seed():
    db = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(User).first():
            print("Already seeded.")
            return

        user = User(email="you@example.com")
        db.add(user)
        db.flush()  # flush assigns the UUID without committing

        entity = Entity(
            user_id=user.id,
            entity_type="APPLICATION",
            title="Palantir — Forward Deployed Engineer",
            current_state="APPLIED",
        )
        db.add(entity)
        db.flush()

        application = Application(
            entity_id=entity.id,
            company="Palantir",
            role="Forward Deployed Engineer",
        )
        db.add(application)
        db.commit()
        print(f"Seeded user {user.id}, application {entity.id}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()