"""Модели SQLAlchemy для базы данных риелторского сайта."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Agent(Base):
    """Агент (риелтор)."""

    __tablename__ = "agents"
    __table_args__ = (
        CheckConstraint(
            "commission_percent >= 0 AND commission_percent <= 100",
            name="ck_agents_commission",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    commission_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    properties: Mapped[list["Property"]] = relationship(back_populates="agent")
    deals: Mapped[list["Deal"]] = relationship(back_populates="agent")


class Client(Base):
    """Клиент."""

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), unique=True, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    deals: Mapped[list["Deal"]] = relationship(back_populates="client")


class Property(Base):
    """Объект недвижимости."""

    __tablename__ = "properties"
    __table_args__ = (
        CheckConstraint(
            "property_type IN ('flat', 'house', 'land', 'commercial')",
            name="ck_properties_property_type",
        ),
        CheckConstraint(
            "operation_type IN ('sale', 'rent')",
            name="ck_properties_operation_type",
        ),
        CheckConstraint(
            "status IN ('available', 'reserved', 'archived')",
            name="ck_properties_status",
        ),
        CheckConstraint("price >= 0", name="ck_properties_price"),
        CheckConstraint("rooms >= 0", name="ck_properties_rooms"),
        CheckConstraint("area >= 0", name="ck_properties_area"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    property_type: Mapped[str] = mapped_column(String(20), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(10), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, index=True)
    rooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="available", index=True
    )
    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    agent: Mapped["Agent"] = relationship(back_populates="properties")
    deals: Mapped[list["Deal"]] = relationship(back_populates="property")


class Deal(Base):
    """Сделка."""

    __tablename__ = "deals"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'completed', 'cancelled')",
            name="ck_deals_status",
        ),
        CheckConstraint("price >= 0", name="ck_deals_price"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    deal_date: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("CURRENT_DATE")
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    property: Mapped["Property"] = relationship(back_populates="deals")
    client: Mapped["Client"] = relationship(back_populates="deals")
    agent: Mapped["Agent"] = relationship(back_populates="deals")
