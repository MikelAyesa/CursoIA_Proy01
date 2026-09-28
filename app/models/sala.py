from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Integer, String, UniqueConstraint, event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text, TypeDecorator

from app.models.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SalaEstado(str, Enum):
    disponible = "disponible"
    mantenimiento = "mantenimiento"
    inactiva = "inactiva"


class JSONList(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: list[str] | None, dialect: object) -> str:
        return json.dumps(value or [], ensure_ascii=False)

    def process_result_value(self, value: str | None, dialect: object) -> list[str]:
        if not value:
            return []
        return json.loads(value)


class Sala(Base):
    __tablename__ = "salas"
    __table_args__ = (UniqueConstraint("nombre_normalizado", name="uq_salas_nombre_normalizado"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    nombre_normalizado: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    capacidad: Mapped[int] = mapped_column(Integer, nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(150), nullable=False)
    ubicacion_normalizada: Mapped[str] = mapped_column(String(150), nullable=False)
    equipamiento: Mapped[list[str]] = mapped_column(JSONList(), nullable=False, default=list)
    estado: Mapped[SalaEstado] = mapped_column(
        SqlEnum(
            SalaEstado,
            native_enum=False,
            values_callable=lambda values: [value.value for value in values],
            length=20,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=SalaEstado.disponible,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


@event.listens_for(Sala, "before_insert")
@event.listens_for(Sala, "before_update")
def sync_normalized_name(mapper: object, connection: object, target: Sala) -> None:
    target.nombre = target.nombre.strip()
    target.nombre_normalizado = target.nombre.lower()
    target.ubicacion = target.ubicacion.strip()
    target.ubicacion_normalizada = target.ubicacion.lower()
