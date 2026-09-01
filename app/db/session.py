# # checking session that is postgres connected to fastapi with session maker and create engine
# import os

# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# load_dotenv()


# DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     raise RuntimeError("Database is not cofigured")
# engine=create_engine(
#     DATABASE_URL,
#     pool_pre_ping=True #Connection Health Check".,
# )#apke app me kabhi OperationalError: server closed the connection unexpectedly wala crash nahi aayega.

# sessionmaker(bind=engine,
#             autoflush=False,
#             autocommit=False,
            # )
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()