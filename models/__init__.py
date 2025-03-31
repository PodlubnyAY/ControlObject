import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Настройка базы данных
db_path = Path(os.getenv('APPDATA'), 'TTPOSU')
db_path.mkdir(exist_ok=True)
db_path /= 'database.db'
DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

from . import users
from . import entries
from .filter import FilterProxyModel

Base.metadata.create_all(engine)
