import pytest
from sqlalchemy.orm import Session

from app.exceptions import ConflictError
from app.models.sala import SalaEstado
from app.schemas.sala import SalaCreate, SalaUpdate
from app.services.sala_service import SalaService


class ReservationCheckerStub:
    def __init__(self, has_reservations: bool) -> None:
        self.has_reservations = has_reservations

    def has_future_reservations(self, db: Session, sala_id: int) -> bool:
        return self.has_reservations


def test_delete_marks_room_as_inactive(db_session: Session) -> None:
    service = SalaService(db_session)
    sala = service.create(
        SalaCreate(
            nombre="Sala Azul",
            descripcion="Sala grande",
            capacidad=14,
            ubicacion="Donostia",
            equipamiento=["Pantalla", "Pizarra"],
        )
    )

    service.delete(sala.id)

    updated = service.get_by_id(sala.id)
    assert updated.estado == SalaEstado.inactiva


def test_update_to_inactive_conflicts_when_future_reservations_exist(db_session: Session) -> None:
    service = SalaService(db_session, reservation_checker=ReservationCheckerStub(True))
    sala = service.create(
        SalaCreate(
            nombre="Sala Verde",
            descripcion=None,
            capacidad=8,
            ubicacion="Vitoria",
            equipamiento=[],
        )
    )

    with pytest.raises(ConflictError) as exc_info:
        service.update(sala.id, SalaUpdate(estado=SalaEstado.inactiva))

    assert "reservas futuras" in exc_info.value.detail
