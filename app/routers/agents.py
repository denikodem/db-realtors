"""Роутер агентов: CRUD через HTML-формы."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app import crud
from app.templating import templates
from app.routers.properties import parse_decimal

router = APIRouter(prefix="/agents", tags=["agents"])


def read_agent_form(form):
    full_name = (form.get("full_name") or "").strip()
    phone = (form.get("phone") or "").strip()
    email = (form.get("email") or "").strip() or None
    commission = parse_decimal(form.get("commission_percent"))

    errors = []
    if not full_name:
        errors.append("Заполните ФИО агента.")
    if not phone:
        errors.append("Заполните телефон.")
    if commission is None:
        errors.append("Укажите процент комиссии (число от 0 до 100).")
    elif commission < 0 or commission > 100:
        errors.append("Процент комиссии должен быть от 0 до 100.")
    if errors:
        return None, " ".join(errors)

    data = {
        "full_name": full_name,
        "phone": phone,
        "email": email,
        "commission_percent": commission,
    }
    return data, None


def render_form(request, *, mode, agent, form_data, error, status_code=200):
    return templates.TemplateResponse(
        request,
        "agents/form.html",
        {
            "mode": mode,
            "agent": agent,
            "form_data": form_data or {},
            "error": error,
        },
        status_code=status_code,
    )


@router.get("", name="agents.list")
def list_agents(request: Request, db: Session = Depends(get_db)):
    agents = crud.list_agents(db)
    return templates.TemplateResponse(
        request, "agents/list.html", {"agents": agents}
    )


@router.get("/new", name="agents.new")
def new_agent(request: Request):
    return render_form(request, mode="create", agent=None, form_data={}, error=None)


@router.post("", name="agents.create")
async def create_agent(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    data, error = read_agent_form(form)
    if error:
        return render_form(request, mode="create", agent=None,
                           form_data=dict(form), error=error, status_code=400)
    try:
        agent = crud.create_agent(db, **data)
    except IntegrityError:
        db.rollback()
        return render_form(request, mode="create", agent=None,
                           form_data=dict(form),
                           error="Агент с таким e-mail уже существует.",
                           status_code=400)
    return RedirectResponse(
        url=request.url_for("agents.detail", agent_id=agent.id), status_code=303
    )


@router.get("/{agent_id}", name="agents.detail")
def agent_detail(request: Request, agent_id: int, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    if agent is None:
        return HTMLResponse("<h1>404</h1><p>Агент не найден.</p>", status_code=404)
    return templates.TemplateResponse(
        request, "agents/detail.html", {"agent": agent}
    )


@router.get("/{agent_id}/edit", name="agents.edit")
def edit_agent(request: Request, agent_id: int, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    if agent is None:
        return HTMLResponse("<h1>404</h1><p>Агент не найден.</p>", status_code=404)
    return render_form(request, mode="edit", agent=agent, form_data={}, error=None)


@router.post("/{agent_id}/edit", name="agents.update")
async def update_agent(request: Request, agent_id: int, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    if agent is None:
        return HTMLResponse("<h1>404</h1><p>Агент не найден.</p>", status_code=404)
    form = await request.form()
    data, error = read_agent_form(form)
    if error:
        return render_form(request, mode="edit", agent=None,
                           form_data=dict(form), error=error, status_code=400)
    try:
        crud.update_agent(db, agent, **data)
    except IntegrityError:
        db.rollback()
        return render_form(request, mode="edit", agent=None,
                           form_data=dict(form),
                           error="Агент с таким e-mail уже существует.",
                           status_code=400)
    return RedirectResponse(
        url=request.url_for("agents.detail", agent_id=agent.id), status_code=303
    )


@router.post("/{agent_id}/delete", name="agents.delete")
def delete_agent(request: Request, agent_id: int, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    if agent is None:
        return HTMLResponse("<h1>404</h1><p>Агент не найден.</p>", status_code=404)
    try:
        crud.delete_agent(db, agent)
    except IntegrityError:
        db.rollback()
        return HTMLResponse(
            "<h1>Удаление невозможно</h1>"
            "<p>Нельзя удалить агента, потому что на него есть связанные объекты "
            "или сделки. Сначала удалите или переназначьте связанные записи.</p>",
            status_code=400,
        )
    return RedirectResponse(url=request.url_for("agents.list"), status_code=303)
