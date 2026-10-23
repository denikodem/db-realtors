"""Роутер главной страницы."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app import crud
from app.templating import templates

router = APIRouter()


@router.get("/", name="home.index")
def index(request: Request, db: Session = Depends(get_db)):
    by_status = crud.count_properties_by_status(db)
    stats = {
        "total": sum(by_status.values()),
        "available": by_status.get("available", 0),
        "reserved": by_status.get("reserved", 0),
        "archived": by_status.get("archived", 0),
        "deals": crud.count_deals(db),
    }
    recent = crud.recent_properties(db, limit=5)
    return templates.TemplateResponse(
        request, "index.html", {"stats": stats, "recent": recent}
    )
