from app.main import app
from app.routers.salas import get_sala_service
from app.schemas.sala import SalaCreate
from app.services.sala_service import SalaService


def test_create_sala_returns_201(client) -> None:
    response = client.post(
        "/api/salas",
        json={
            "nombre": " Sala Norte ",
            "descripcion": " Sala principal ",
            "capacidad": 12,
            "ubicacion": " Bilbao ",
            "equipamiento": ["Pantalla", "pantalla", " Pizarra "],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Sala Norte"
    assert body["descripcion"] == "Sala principal"
    assert body["ubicacion"] == "Bilbao"
    assert body["equipamiento"] == ["pantalla", "pizarra"]
    assert body["estado"] == "disponible"


def test_duplicate_name_returns_409(client) -> None:
    payload = {
        "nombre": "Sala Norte",
        "descripcion": "Primera",
        "capacidad": 12,
        "ubicacion": "Bilbao",
        "equipamiento": ["pantalla"],
    }
    client.post("/api/salas", json=payload)

    response = client.post("/api/salas", json={**payload, "nombre": "sala norte"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Ya existe una sala con ese nombre."}


def test_list_and_filter_rooms(client) -> None:
    client.post(
        "/api/salas",
        json={"nombre": "Sala Norte", "descripcion": None, "capacidad": 12, "ubicacion": "Bilbao", "equipamiento": [], "estado": "disponible"},
    )
    client.post(
        "/api/salas",
        json={"nombre": "Sala Sur", "descripcion": None, "capacidad": 4, "ubicacion": "Madrid", "equipamiento": [], "estado": "mantenimiento"},
    )

    response = client.get("/api/salas?estado=disponible&ubicacion=bil&capacidad_minima=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Sala Norte"


def test_get_existing_and_missing_room(client) -> None:
    created = client.post(
        "/api/salas",
        json={"nombre": "Sala Este", "descripcion": None, "capacidad": 6, "ubicacion": "Pamplona", "equipamiento": []},
    ).json()

    found = client.get(f"/api/salas/{created['id']}")
    missing = client.get("/api/salas/999")

    assert found.status_code == 200
    assert found.json()["nombre"] == "Sala Este"
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Sala no encontrada."}


def test_invalid_payload_returns_422(client) -> None:
    response = client.post(
        "/api/salas",
        json={"nombre": "AB", "descripcion": None, "capacidad": 0, "ubicacion": "A", "equipamiento": [""], "estado": "rota"},
    )

    assert response.status_code == 422


def test_update_room_and_conflicts(client) -> None:
    first = client.post(
        "/api/salas",
        json={"nombre": "Sala Uno", "descripcion": None, "capacidad": 10, "ubicacion": "Bilbao", "equipamiento": []},
    ).json()
    second = client.post(
        "/api/salas",
        json={"nombre": "Sala Dos", "descripcion": None, "capacidad": 8, "ubicacion": "Vitoria", "equipamiento": []},
    ).json()

    updated = client.put(f"/api/salas/{first['id']}", json={"descripcion": "Actualizada", "capacidad": 20})
    missing = client.put("/api/salas/999", json={"descripcion": "Actualizada"})
    conflict = client.put(f"/api/salas/{second['id']}", json={"nombre": "SALA UNO"})

    assert updated.status_code == 200
    assert updated.json()["descripcion"] == "Actualizada"
    assert updated.json()["capacidad"] == 20
    assert missing.status_code == 404
    assert conflict.status_code == 409


def test_update_room_can_clear_description_with_null(client) -> None:
    created = client.post(
        "/api/salas",
        json={"nombre": "Sala Limpia", "descripcion": "Temporal", "capacidad": 7, "ubicacion": "Bilbao", "equipamiento": []},
    ).json()

    updated = client.put(f"/api/salas/{created['id']}", json={"descripcion": None})

    assert updated.status_code == 200
    assert updated.json()["descripcion"] is None


def test_update_room_without_description_keeps_existing_value(client) -> None:
    created = client.post(
        "/api/salas",
        json={"nombre": "Sala Persistente", "descripcion": "Se mantiene", "capacidad": 11, "ubicacion": "Bilbao", "equipamiento": []},
    ).json()

    updated = client.put(f"/api/salas/{created['id']}", json={"capacidad": 13})

    assert updated.status_code == 200
    assert updated.json()["descripcion"] == "Se mantiene"


def test_delete_valid_room_returns_204_and_marks_inactive(client) -> None:
    created = client.post(
        "/api/salas",
        json={"nombre": "Sala Borrable", "descripcion": None, "capacidad": 9, "ubicacion": "Bilbao", "equipamiento": []},
    ).json()

    deleted = client.delete(f"/api/salas/{created['id']}")
    fetched = client.get(f"/api/salas/{created['id']}")

    assert deleted.status_code == 204
    assert fetched.status_code == 200
    assert fetched.json()["estado"] == "inactiva"


def test_delete_with_future_reservations_returns_409(client, db_session) -> None:
    class ReservationCheckerStub:
        def has_future_reservations(self, db, sala_id: int) -> bool:
            return True

    sala = SalaService(db_session).create(
        SalaCreate(nombre="Sala Reservada", descripcion=None, capacidad=10, ubicacion="Bilbao", equipamiento=[])
    )

    def override_service():
        return SalaService(db_session, reservation_checker=ReservationCheckerStub())

    app.dependency_overrides[get_sala_service] = override_service
    try:
        response = client.delete(f"/api/salas/{sala.id}")
    finally:
        app.dependency_overrides.pop(get_sala_service, None)

    assert response.status_code == 409
    assert response.json() == {"detail": "No se puede eliminar la sala porque tiene reservas futuras."}
