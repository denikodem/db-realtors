"""Настройка Jinja2-шаблонов в отдельном модуле, чтобы не было циклических импортов."""
from pathlib import Path

from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=BASE_DIR / "templates")
