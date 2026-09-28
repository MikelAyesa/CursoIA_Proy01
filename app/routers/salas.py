from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sala import SalaEstado
from app.schemas.sala import SalaCreate, SalaResponse, SalaUpdate
from app.services.sala_service import SalaService

router = APIRouter(prefix="/api/salas", tags=["salas"])


def get_sala_service(db: Session = Depends(get_db)) -> SalaService:
    return SalaService(db)


@router.get("", response_model=list[SalaResponse], status_code=status.HTTP_200_OK)
def list_salas(
    estado: SalaEstado | None = Query(default=None),
    ubicacion: str | None = Query(default=None),
    capacidad_minima: Annotated[int | None, Query(ge=1, le=1000)] = None,
    service: SalaService = Depends(get_sala_service),
) -> list[SalaResponse]:
    return service.get_all(estado=estado, ubicacion=ubicacion, capacidad_minima=capacidad_minima)


@router.get("/{sala_id}", response_model=SalaResponse, status_code=status.HTTP_200_OK)
def get_sala(sala_id: Annotated[int, Path(ge=1)], service: SalaService = Depends(get_sala_service)) -> SalaResponse:
    return service.get_by_id(sala_id)


@router.post("", response_model=SalaResponse, status_code=status.HTTP_201_CREATED)
def create_sala(payload: SalaCreate, service: SalaService = Depends(get_sala_service)) -> SalaResponse:
    return service.create(payload)


@router.put(
    "/{sala_id}",
    response_model=SalaResponse,
    status_code=status.HTTP_200_OK,
    description="Acepta actualización parcial: los campos omitidos conservan su valor actual.",
)
def update_sala(
    sala_id: Annotated[int, Path(ge=1)],
    payload: SalaUpdate,
    service: SalaService = Depends(get_sala_service),
) -> SalaResponse:
    return service.update(sala_id, payload)


@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sala(sala_id: Annotated[int, Path(ge=1)], service: SalaService = Depends(get_sala_service)) -> Response:
    service.delete(sala_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
