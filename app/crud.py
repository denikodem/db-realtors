"""Функции для работы с базой данных (простой CRUD без лишних абстракций)."""
from decimal import Decimal

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app import models


# ---------- Агенты ----------

def list_agents(db: Session) -> list[models.Agent]:
    return db.query(models.Agent).order_by(models.Agent.full_name).all()


def get_agent(db: Session, agent_id: int) -> models.Agent | None:
    return db.get(models.Agent, agent_id)


def create_agent(db: Session, *, full_name: str, phone: str,
                 email: str | None, commission_percent: Decimal) -> models.Agent:
    agent = models.Agent(
        full_name=full_name,
        phone=phone,
        email=email,
        commission_percent=commission_percent,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def update_agent(db: Session, agent: models.Agent, *, full_name: str, phone: str,
                 email: str | None, commission_percent: Decimal) -> models.Agent:
    agent.full_name = full_name
    agent.phone = phone
    agent.email = email
    agent.commission_percent = commission_percent
    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent: models.Agent) -> None:
    db.delete(agent)
    db.commit()


# ---------- Клиенты ----------

def list_clients(db: Session) -> list[models.Client]:
    return db.query(models.Client).order_by(models.Client.full_name).all()


def get_client(db: Session, client_id: int) -> models.Client | None:
    return db.get(models.Client, client_id)


def create_client(db: Session, *, full_name: str, phone: str,
                  email: str | None, notes: str | None) -> models.Client:
    client = models.Client(
        full_name=full_name,
        phone=phone,
        email=email,
        notes=notes,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update_client(db: Session, client: models.Client, *, full_name: str, phone: str,
                  email: str | None, notes: str | None) -> models.Client:
    client.full_name = full_name
    client.phone = phone
    client.email = email
    client.notes = notes
    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client: models.Client) -> None:
    db.delete(client)
    db.commit()


# ---------- Объекты недвижимости ----------

def list_properties(db: Session, *, query: str | None = None,
                    operation_type: str | None = None,
                    property_type: str | None = None,
                    district: str | None = None,
                    max_price: Decimal | None = None) -> list[models.Property]:
    q = db.query(models.Property).options(joinedload(models.Property.agent))
    if query:
        like = f"%{query}%"
        q = q.filter(or_(models.Property.title.ilike(like),
                         models.Property.address.ilike(like)))
    if operation_type:
        q = q.filter(models.Property.operation_type == operation_type)
    if property_type:
        q = q.filter(models.Property.property_type == property_type)
    if district:
        q = q.filter(models.Property.district == district)
    if max_price is not None:
        q = q.filter(models.Property.price <= max_price)
    return q.order_by(models.Property.created_at.desc(), models.Property.id.desc()).all()


def get_property(db: Session, property_id: int) -> models.Property | None:
    return (
        db.query(models.Property)
        .options(joinedload(models.Property.agent))
        .get(property_id)
    )


def create_property(db: Session, data: dict) -> models.Property:
    prop = models.Property(**data)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


def update_property(db: Session, prop: models.Property, data: dict) -> models.Property:
    for key, value in data.items():
        setattr(prop, key, value)
    db.commit()
    db.refresh(prop)
    return prop


def delete_property(db: Session, prop: models.Property) -> None:
    db.delete(prop)
    db.commit()


def count_properties_by_status(db: Session) -> dict[str, int]:
    rows = (
        db.query(models.Property.status, func.count(models.Property.id))
        .group_by(models.Property.status)
        .all()
    )
    return {status: cnt for status, cnt in rows}


def recent_properties(db: Session, limit: int = 5) -> list[models.Property]:
    return (
        db.query(models.Property)
        .options(joinedload(models.Property.agent))
        .order_by(models.Property.created_at.desc(), models.Property.id.desc())
        .limit(limit)
        .all()
    )


# ---------- Сделки ----------

def list_deals(db: Session) -> list[models.Deal]:
    return (
        db.query(models.Deal)
        .options(joinedload(models.Deal.property),
                 joinedload(models.Deal.client),
                 joinedload(models.Deal.agent))
        .order_by(models.Deal.deal_date.desc(), models.Deal.id.desc())
        .all()
    )


def create_deal(db: Session, data: dict) -> models.Deal:
    deal = models.Deal(**data)
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


def count_deals(db: Session) -> int:
    return db.query(func.count(models.Deal.id)).scalar()
