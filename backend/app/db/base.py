from sqlalchemy.orm import DeclarativeBase

# All models inherit from this Base.
# Alembic uses Base.metadata to discover tables and generate migrations.
class Base(DeclarativeBase):
    pass