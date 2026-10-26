"""Роутер сделок: просмотр списка, создание и удаление сделки."""
from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app import crud
from app.templating import templates
from app.routers.properties import parse_decimal

router = APIRouter(prefix="/deals", tags=["deals"])

DEAL_STATUSES = {"draft": "Черновик", "completed": "Завершена", "cancelled": "Отменена"}


@router.get("", name="deals.list")
def list_deals(request: Request, db: Session = Depends(get_db)):
    deals = crud.list_deals(db)
    return templates.TemplateResponse(
        request, "deals/list.html", {"deals": deals, "deal_statuses": DEAL_STATUSES}
    )


@router.get("/new", name="deals.new")
def new_deal(request: Request, db: Session = Depends(get_db)):
    return render_deal_form(
        request, db, form_data={}, error=None, status_code=200
    )


def render_deal_form(request, db, *, form_data, error, status_code=200):
    return templates.TemplateResponse(
        request,
        "deals/form.html",
        {
            "properties": crud.list_properties(db),
            "clients": crud.list_clients(db),
            "agents": crud.list_agents(db),
            "form_data": form_data,
            "error": error,
            "deal_statuses": DEAL_STATUSES,
            "today": date.today().isoformat(),
        },
        status_code=status_code,
    )


@router.post("", name="deals.create")
async def create_deal(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    form_data = {key: form.get(key, "") for key in form.keys()}

    property_id = (form.get("property_id") or "").strip()
    client_id = (form.get("client_id") or "").strip()
    agent_id = (form.get("agent_id") or "").strip()
    deal_date_raw = (form.get("deal_date") or "").strip()
    price = parse_decimal(form.get("price"))
    status = form.get("status") or "draft"

    errors = []

    prop = crud.get_property(db, int(property_id)) if property_id.isdigit() else None
    if prop is None:
        errors.append("Выберите объект недвижимости из списка.")
    elif prop.status == "archived":
        errors.append("Нельзя оформить сделку по объекту, который в архиве.")

    client = crud.get_client(db, int(client_id)) if client_id.isdigit() else None
    if client is None:
        errors.append("Выберите клиента из списка.")

    agent = crud.get_agent(db, int(agent_id)) if agent_id.isdigit() else None
    if agent is None:
        errors.append("Выберите агента из списка.")

    if price is None:
        errors.append("Укажите корректную цену сделки.")
    elif price < 0:
        errors.append("Цена сделки не может быть отрицательной.")

    if status not in DEAL_STATUSES:
        errors.append("Выберите статус сделки.")

    deal_date = None
    if deal_date_raw:
        try:
            deal_date = date.fromisoformat(deal_date_raw)
        except ValueError:
            errors.append("Дата сделки указана в неверном формате.")
    else:
        deal_date = date.today()

    if errors:
        return render_deal_form(request, db, form_data=form_data,
                                error=" ".join(errors), status_code=400)

    deal = crud.create_deal(
        db,
        {
            "property_id": prop.id,
            "client_id": client.id,
            "agent_id": agent.id,
            "deal_date": deal_date,
            "price": price,
            "status": status,
        },
    )
    return RedirectResponse(url=request.url_for("deals.list"), status_code=303)


@router.post("/{deal_id}/delete", name="deals.delete")
def delete_deal(request: Request, deal_id: int, db: Session = Depends(get_db)):
    deal = crud.get_deal(db, deal_id)
    if deal is None:
        return HTMLResponse("<h1>404</h1><p>Сделка не найдена.</p>", status_code=404)
    try:
        crud.delete_deal(db, deal)
    except IntegrityError:
        db.rollback()
        return HTMLResponse(
            "<h1>Удаление невозможно</h1>"
            "<p>Не удалось удалить сделку из-за связанных данных в базе.</p>",
            status_code=400,
        )
    return RedirectResponse(url=request.url_for("deals.list"), status_code=303)
