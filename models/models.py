from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Настройка базы данных
DATABASE_URL = "sqlite:///demo2.db"
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

Session = sessionmaker(bind=engine)
