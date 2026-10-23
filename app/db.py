"""Настройка подключения к PostgreSQL через SQLAlchemy."""
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print(
        "Не задан DATABASE_URL. Скопируй .env.example в .env и укажи "
        "подключение к PostgreSQL.",
        file=sys.stderr,
    )
    sys.exit(1)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
except Exception as exc:  # например, неверный URL подключения
    print(f"Не удалось создать движок БД по DATABASE_URL: {exc}", file=sys.stderr)
    sys.exit(1)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Зависимость FastAPI: даёт сессию БД на время запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Создаёт таблицы, если их ещё нет."""
    from app import models  # noqa: F401  (чтобы модели зарегистрировались)

    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        print(
            f"Не удалось подключиться к PostgreSQL и создать таблицы: {exc}\n"
            "Проверь DATABASE_URL в файле .env и что сервер PostgreSQL запущен.",
            file=sys.stderr,
        )
        sys.exit(1)
