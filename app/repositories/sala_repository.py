from __future__ import annotations

from typing import Protocol

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.sala import Sala, SalaEstado


class ReservationChecker(Protocol):
    def has_future_reservations(self, db: Session, sala_id: int) -> bool: ...


class NullReservationChecker:
    """
    Implementación temporal mientras no exista el módulo de reservas.

    Devuelve siempre False porque actualmente no se persisten reservas en este proyecto.
    La eliminación es lógica, por lo que los datos de la sala se conservan incluso antes
    de integrar la comprobación real de reservas futuras.
    """

    def has_future_reservations(self, db: Session, sala_id: int) -> bool:
        return False


class SalaRepository:
    def __init__(self, db: Session, reservation_checker: ReservationChecker | None = None) -> None:
        self.db = db
        self.reservation_checker = reservation_checker or NullReservationChecker()

    def get_all(
        self,
        *,
        estado: SalaEstado | None = None,
        ubicacion: str | None = None,
        capacidad_minima: int | None = None,
    ) -> list[Sala]:
        query: Select[tuple[Sala]] = select(Sala).order_by(Sala.id)

        if estado is not None:
            query = query.where(Sala.estado == estado)
        if ubicacion:
            query = query.where(Sala.ubicacion_normalizada.contains(ubicacion.strip().lower()))
        if capacidad_minima is not None:
            query = query.where(Sala.capacidad >= capacidad_minima)

        return list(self.db.scalars(query).all())

    def get_by_id(self, sala_id: int) -> Sala | None:
        return self.db.get(Sala, sala_id)

    def get_by_name(self, nombre: str) -> Sala | None:
        normalized = nombre.strip().lower()
        query = select(Sala).where(Sala.nombre_normalizado == normalized)
        return self.db.scalar(query)

    def create(self, payload: dict) -> Sala:
        sala = Sala(**payload)
        self.db.add(sala)
        self.db.flush()
        self.db.refresh(sala)
        return sala

    def update(self, sala: Sala, payload: dict) -> Sala:
        for key, value in payload.items():
            setattr(sala, key, value)
        self.db.flush()
        self.db.refresh(sala)
        return sala

    def deactivate(self, sala: Sala) -> Sala:
        sala.estado = SalaEstado.inactiva
        self.db.flush()
        self.db.refresh(sala)
        return sala

    def has_future_reservations(self, sala_id: int) -> bool:
        return self.reservation_checker.has_future_reservations(self.db, sala_id)
