"""Простые Pydantic-схемы. Используются минимально, в основном для чтения данных."""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    phone: str
    email: str | None = None
    commission_percent: Decimal


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    phone: str
    email: str | None = None
    notes: str | None = None


class PropertyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    property_type: str
    operation_type: str
    address: str
    district: str | None = None
    price: Decimal
    status: str
    created_at: datetime


class DealRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deal_date: date
    price: Decimal
    status: str
