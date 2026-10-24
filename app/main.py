"""Главный файл приложения FastAPI."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.templating import templates
from app.routers import agents, clients, home

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Риелторские услуги",
    description="Учебный проект по базам данных: сайт агентства недвижимости.",
)

# Статика и шаблоны
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Роутеры
app.include_router(home.router)
app.include_router(agents.router)
app.include_router(clients.router)


@app.on_event("startup")
def startup() -> None:
    """При запуске создаём таблицы в PostgreSQL."""
    init_db()
