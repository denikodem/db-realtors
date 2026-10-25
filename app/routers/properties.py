"""Роутер объектов недвижимости: список с фильтрами, CRUD через HTML-формы."""
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app import crud
from app.templating import templates

router = APIRouter(prefix="/properties", tags=["properties"])

PROPERTY_TYPES = {
    "flat": "Квартира",
    "house": "Дом",
    "land": "Земельный участок",
    "commercial": "Коммерция",
}
OPERATION_TYPES = {"sale": "Продажа", "rent": "Аренда"}
STATUSES = {"available": "Доступен", "reserved": "Зарезервирован", "archived": "Архив"}


def parse_decimal(value: str | None) -> Decimal | None:
    """Превращает строку формы в Decimal или возвращает None, если пусто/некорректно."""
    value = (value or "").strip().replace(",", ".")
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def form_fields_to_dict(form) -> dict:
    """Для повторной отрисовки формы: строковые значения полей."""
    return {
        "title": form.get("title", ""),
        "description": form.get("description", ""),
        "property_type": form.get("property_type", ""),
        "operation_type": form.get("operation_type", ""),
        "address": form.get("address", ""),
        "district": form.get("district", ""),
        "price": form.get("price", ""),
        "rooms": form.get("rooms", ""),
        "area": form.get("area", ""),
        "status": form.get("status", "available"),
        "agent_id": form.get("agent_id", ""),
    }


@router.get("", name="properties.list")
def list_properties(
    request: Request,
    db: Session = Depends(get_db),
    query: str | None = None,
    operation_type: str | None = None,
    property_type: str | None = None,
    district: str | None = None,
    max_price: str | None = None,
):
    max_price_dec = parse_decimal(max_price)
    props = crud.list_properties(
        db,
        query=(query or "").strip() or None,
        operation_type=operation_type or None,
        property_type=property_type or None,
        district=(district or "").strip() or None,
        max_price=max_price_dec,
    )
    return templates.TemplateResponse(
        request,
        "properties/list.html",
        {
            "properties": props,
            "query": query or "",
            "operation_type": operation_type or "",
            "property_type": property_type or "",
            "district": district or "",
            "max_price": max_price or "",
            "property_types": PROPERTY_TYPES,
            "operation_types": OPERATION_TYPES,
            "statuses": STATUSES,
        },
    )


@router.get("/new", name="properties.new")
def new_property(request: Request, db: Session = Depends(get_db)):
    agents = crud.list_agents(db)
    return templates.TemplateResponse(
        request,
        "properties/form.html",
        {
            "mode": "create",
            "prop": None,
            "form_data": {},
            "agents": agents,
            "error": None,
            "property_types": PROPERTY_TYPES,
            "operation_types": OPERATION_TYPES,
            "statuses": STATUSES,
        },
    )


def read_property_form(form, db: Session):
    """Читает и проверяет форму объекта. Возвращает (data, error)."""
    title = (form.get("title") or "").strip()
    address = (form.get("address") or "").strip()
    agent_id_raw = (form.get("agent_id") or "").strip()
    price = parse_decimal(form.get("price"))

    property_type = form.get("property_type") or ""
    operation_type = form.get("operation_type") or ""
    status = form.get("status") or "available"

    rooms_raw = (form.get("rooms") or "").strip()
    area = parse_decimal(form.get("area"))

    rooms = None
    if rooms_raw:
        try:
            rooms = int(rooms_raw)
        except ValueError:
            return None, "Количество комнат должно быть целым числом."

    errors = []
    if not title:
        errors.append("Заполните название объекта.")
    if not address:
        errors.append("Заполните адрес.")
    if price is None:
        errors.append("Укажите корректную цену.")
    elif price < 0:
        errors.append("Цена не может быть отрицательной.")
    if area is not None and area < 0:
        errors.append("Площадь не может быть отрицательной.")
    if rooms is not None and rooms < 0:
        errors.append("Количество комнат не может быть отрицательным.")
    if property_type not in PROPERTY_TYPES:
        errors.append("Выберите тип объекта.")
    if operation_type not in OPERATION_TYPES:
        errors.append("Выберите тип операции.")
    if status not in STATUSES:
        errors.append("Выберите статус объекта.")
    if not agent_id_raw.isdigit() or crud.get_agent(db, int(agent_id_raw)) is None:
        errors.append("Выберите агента из списка.")

    if errors:
        return None, " ".join(errors)

    data = {
        "title": title,
        "description": (form.get("description") or "").strip() or None,
        "property_type": property_type,
        "operation_type": operation_type,
        "address": address,
        "district": (form.get("district") or "").strip() or None,
        "price": price,
        "rooms": rooms,
        "area": area,
        "status": status,
        "agent_id": int(agent_id_raw),
    }
    return data, None


@router.post("", name="properties.create")
async def create_property(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    data, error = read_property_form(form, db)
    if error:
        agents = crud.list_agents(db)
        return templates.TemplateResponse(
            request,
            "properties/form.html",
            {
                "mode": "create",
                "prop": None,
                "form_data": form_fields_to_dict(form),
                "agents": agents,
                "error": error,
                "property_types": PROPERTY_TYPES,
                "operation_types": OPERATION_TYPES,
                "statuses": STATUSES,
            },
            status_code=400,
        )
    prop = crud.create_property(db, data)
    return RedirectResponse(
        url=request.url_for("properties.detail", property_id=prop.id), status_code=303
    )


@router.get("/{property_id}", name="properties.detail")
def property_detail(request: Request, property_id: int, db: Session = Depends(get_db)):
    prop = crud.get_property(db, property_id)
    if prop is None:
        return HTMLResponse("<h1>404</h1><p>Объект не найден.</p>", status_code=404)
    return templates.TemplateResponse(
        request,
        "properties/detail.html",
        {
            "prop": prop,
            "property_types": PROPERTY_TYPES,
            "operation_types": OPERATION_TYPES,
            "statuses": STATUSES,
        },
    )


@router.get("/{property_id}/edit", name="properties.edit")
def edit_property(request: Request, property_id: int, db: Session = Depends(get_db)):
    prop = crud.get_property(db, property_id)
    if prop is None:
        return HTMLResponse("<h1>404</h1><p>Объект не найден.</p>", status_code=404)
    agents = crud.list_agents(db)
    return templates.TemplateResponse(
        request,
        "properties/form.html",
        {
            "mode": "edit",
            "prop": prop,
            "form_data": {},
            "agents": agents,
            "error": None,
            "property_types": PROPERTY_TYPES,
            "operation_types": OPERATION_TYPES,
            "statuses": STATUSES,
        },
    )


@router.post("/{property_id}/edit", name="properties.update")
async def update_property(request: Request, property_id: int,
                          db: Session = Depends(get_db)):
    prop = crud.get_property(db, property_id)
    if prop is None:
        return HTMLResponse("<h1>404</h1><p>Объект не найден.</p>", status_code=404)
    form = await request.form()
    data, error = read_property_form(form, db)
    if error:
        agents = crud.list_agents(db)
        return templates.TemplateResponse(
            request,
            "properties/form.html",
            {
                "mode": "edit",
                "prop": None,
                "form_data": form_fields_to_dict(form),
                "agents": agents,
                "error": error,
                "property_types": PROPERTY_TYPES,
                "operation_types": OPERATION_TYPES,
                "statuses": STATUSES,
            },
            status_code=400,
        )
    crud.update_property(db, prop, data)
    return RedirectResponse(
        url=request.url_for("properties.detail", property_id=prop.id), status_code=303
    )


@router.post("/{property_id}/delete", name="properties.delete")
def delete_property(request: Request, property_id: int, db: Session = Depends(get_db)):
    prop = crud.get_property(db, property_id)
    if prop is None:
        return HTMLResponse("<h1>404</h1><p>Объект не найден.</p>", status_code=404)
    try:
        crud.delete_property(db, prop)
    except IntegrityError:
        db.rollback()
        return HTMLResponse(
            "<h1>Удаление невозможно</h1>"
            "<p>Нельзя удалить объект, потому что на него есть связанные сделки. "
            "Сначала удалите связанные записи.</p>"
            '<p><a href="' + str(request.url_for("properties.detail", property_id=property_id))
            + '">Назад к объекту</a></p>',
            status_code=400,
        )
    return RedirectResponse(url=request.url_for("properties.list"), status_code=303)
