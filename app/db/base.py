import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass



load_dotenv()

engine = create_engine(os.environ['DATABASE_URL'])