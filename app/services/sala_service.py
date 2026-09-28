from __future__ import annotations

from collections.abc import Callable

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError, PersistenceError
from app.models.sala import Sala, SalaEstado
from app.repositories.sala_repository import ReservationChecker, SalaRepository
from app.schemas.sala import SalaCreate, SalaUpdate


class SalaService:
    def __init__(self, db: Session, reservation_checker: ReservationChecker | None = None) -> None:
        self.db = db
        self.repository = SalaRepository(db, reservation_checker=reservation_checker)

    def get_all(
        self,
        *,
        estado: SalaEstado | None = None,
        ubicacion: str | None = None,
        capacidad_minima: int | None = None,
    ) -> list[Sala]:
        return self.repository.get_all(estado=estado, ubicacion=ubicacion, capacidad_minima=capacidad_minima)

    def get_by_id(self, sala_id: int) -> Sala:
        sala = self.repository.get_by_id(sala_id)
        if sala is None:
            raise NotFoundError("Sala no encontrada.")
        return sala

    def create(self, payload: SalaCreate) -> Sala:
        data = payload.model_dump()
        self._ensure_unique_name(data["nombre"])
        return self._commit_operation(lambda: self.repository.create(data), duplicate_message="Ya existe una sala con ese nombre.")

    def update(self, sala_id: int, payload: SalaUpdate) -> Sala:
        sala = self.get_by_id(sala_id)
        data = payload.model_dump(exclude_unset=True)

        if "nombre" in data:
            self._ensure_unique_name(data["nombre"], current_id=sala.id)
        if data.get("estado") == SalaEstado.inactiva and sala.estado != SalaEstado.inactiva and self.repository.has_future_reservations(sala.id):
            raise ConflictError("No se puede inactivar la sala porque tiene reservas futuras.")

        if not data:
            return sala

        return self._commit_operation(
            lambda: self.repository.update(sala, data),
            duplicate_message="Ya existe una sala con ese nombre.",
        )

    def delete(self, sala_id: int) -> None:
        sala = self.get_by_id(sala_id)
        if self.repository.has_future_reservations(sala.id):
            raise ConflictError("No se puede eliminar la sala porque tiene reservas futuras.")

        self._commit_operation(lambda: self.repository.deactivate(sala))

    def _ensure_unique_name(self, nombre: str, current_id: int | None = None) -> None:
        existing = self.repository.get_by_name(nombre)
        if existing and existing.id != current_id:
            raise ConflictError("Ya existe una sala con ese nombre.")

    def _commit_operation(self, operation: Callable[[], Sala | None], duplicate_message: str | None = None) -> Sala | None:
        try:
            result = operation()
            self.db.commit()
            if isinstance(result, Sala):
                self.db.refresh(result)
            return result
        except ConflictError:
            self.db.rollback()
            raise
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(duplicate_message or "Conflicto de datos.") from exc
        except SQLAlchemyError as exc:
            self.db.rollback()
            raise PersistenceError("Error inesperado de persistencia.") from exc
