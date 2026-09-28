from sqlalchemy.orm import Session

from app.models.sala import SalaEstado
from app.repositories.sala_repository import SalaRepository


def test_get_by_name_is_case_insensitive(db_session: Session) -> None:
    repository = SalaRepository(db_session)
    repository.create(
        {
            "nombre": "Sala Norte",
            "descripcion": "Principal",
            "capacidad": 10,
            "ubicacion": "Bilbao",
            "equipamiento": ["pantalla"],
            "estado": SalaEstado.disponible,
        }
    )
    db_session.commit()

    sala = repository.get_by_name("sala norte")

    assert sala is not None
    assert sala.nombre == "Sala Norte"


def test_get_all_supports_filters(db_session: Session) -> None:
    repository = SalaRepository(db_session)
    repository.create(
        {
            "nombre": "Sala Norte",
            "descripcion": "Principal",
            "capacidad": 12,
            "ubicacion": "Bilbao",
            "equipamiento": ["pantalla"],
            "estado": SalaEstado.disponible,
        }
    )
    repository.create(
        {
            "nombre": "Sala Sur",
            "descripcion": None,
            "capacidad": 4,
            "ubicacion": "Madrid",
            "equipamiento": [],
            "estado": SalaEstado.mantenimiento,
        }
    )
    db_session.commit()

    result = repository.get_all(estado=SalaEstado.disponible, ubicacion="bil", capacidad_minima=10)

    assert len(result) == 1
    assert result[0].nombre == "Sala Norte"
