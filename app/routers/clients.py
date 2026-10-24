"""Роутер клиентов: CRUD через HTML-формы."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app import crud
from app.templating import templates

router = APIRouter(prefix="/clients", tags=["clients"])


def read_client_form(form):
    full_name = (form.get("full_name") or "").strip()
    phone = (form.get("phone") or "").strip()
    email = (form.get("email") or "").strip() or None
    notes = (form.get("notes") or "").strip() or None

    errors = []
    if not full_name:
        errors.append("Заполните ФИО клиента.")
    if not phone:
        errors.append("Заполните телефон.")
    if errors:
        return None, " ".join(errors)

    data = {"full_name": full_name, "phone": phone, "email": email, "notes": notes}
    return data, None


def render_form(request, *, mode, client, form_data, error, status_code=200):
    return templates.TemplateResponse(
        request,
        "clients/form.html",
        {
            "mode": mode,
            "client": client,
            "form_data": form_data or {},
            "error": error,
        },
        status_code=status_code,
    )


@router.get("", name="clients.list")
def list_clients(request: Request, db: Session = Depends(get_db)):
    clients = crud.list_clients(db)
    return templates.TemplateResponse(
        request, "clients/list.html", {"clients": clients}
    )


@router.get("/new", name="clients.new")
def new_client(request: Request):
    return render_form(request, mode="create", client=None, form_data={}, error=None)


@router.post("", name="clients.create")
async def create_client(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    data, error = read_client_form(form)
    if error:
        return render_form(request, mode="create", client=None,
                           form_data=dict(form), error=error, status_code=400)
    try:
        client = crud.create_client(db, **data)
    except IntegrityError:
        db.rollback()
        return render_form(request, mode="create", client=None,
                           form_data=dict(form),
                           error="Клиент с таким e-mail уже существует.",
                           status_code=400)
    return RedirectResponse(
        url=request.url_for("clients.detail", client_id=client.id), status_code=303
    )


@router.get("/{client_id}", name="clients.detail")
def client_detail(request: Request, client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if client is None:
        return HTMLResponse("<h1>404</h1><p>Клиент не найден.</p>", status_code=404)
    return templates.TemplateResponse(
        request, "clients/detail.html", {"client": client}
    )


@router.get("/{client_id}/edit", name="clients.edit")
def edit_client(request: Request, client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if client is None:
        return HTMLResponse("<h1>404</h1><p>Клиент не найден.</p>", status_code=404)
    return render_form(request, mode="edit", client=client, form_data={}, error=None)


@router.post("/{client_id}/edit", name="clients.update")
async def update_client(request: Request, client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if client is None:
        return HTMLResponse("<h1>404</h1><p>Клиент не найден.</p>", status_code=404)
    form = await request.form()
    data, error = read_client_form(form)
    if error:
        return render_form(request, mode="edit", client=None,
                           form_data=dict(form), error=error, status_code=400)
    try:
        crud.update_client(db, client, **data)
    except IntegrityError:
        db.rollback()
        return render_form(request, mode="edit", client=None,
                           form_data=dict(form),
                           error="Клиент с таким e-mail уже существует.",
                           status_code=400)
    return RedirectResponse(
        url=request.url_for("clients.detail", client_id=client.id), status_code=303
    )


@router.post("/{client_id}/delete", name="clients.delete")
def delete_client(request: Request, client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if client is None:
        return HTMLResponse("<h1>404</h1><p>Клиент не найден.</p>", status_code=404)
    try:
        crud.delete_client(db, client)
    except IntegrityError:
        db.rollback()
        return HTMLResponse(
            "<h1>Удаление невозможно</h1>"
            "<p>Нельзя удалить клиента, потому что на него есть связанные сделки. "
            "Сначала удалите связанные записи.</p>",
            status_code=400,
        )
    return RedirectResponse(url=request.url_for("clients.list"), status_code=303)
