import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

load_dotenv()

username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT")
domain = os.getenv("DOMAIN")

url = f"postgresql://{username}:{password}@{domain}:{db_port}/{db_name}"

engine = create_engine(url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Функція генератор для отримання сесії бази даних.

    Використовується як залежність у FastAPI для отримання сесії
    SQLAlchemy. Після завершення роботи сесія закривається.

    Yields:
        Session: Сесія бази даних SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
