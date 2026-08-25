# Every model inherits from Base, which allows SQLAlchemy to collect their table definitions into:

# Base.metadata

# That's what Alembic will later use for migrations.

from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass

# It is the foundation for all SQLAlchemy models.

# Base
#  ├── Payment
#  ├── Order
#  ├── Incident
#  ├── EligibilityEvaluation
#  ├── Approval
#  └── Resolution