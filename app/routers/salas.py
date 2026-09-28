from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sala import SalaEstado
from app.schemas.sala import SalaCreate, SalaResponse, SalaUpdate
from app.services.sala_service import SalaService

router = APIRouter(prefix="/api/salas", tags=["salas"])


@router.get("", response_model=list[SalaResponse], status_code=status.HTTP_200_OK)
def list_salas(
    estado: SalaEstado | None = Query(default=None),
    ubicacion: str | None = Query(default=None),
    capacidad_minima: Annotated[int | None, Query(ge=1, le=1000)] = None,
    db: Session = Depends(get_db),
) -> list[SalaResponse]:
    service = SalaService(db)
    return service.get_all(estado=estado, ubicacion=ubicacion, capacidad_minima=capacidad_minima)


@router.get("/{sala_id}", response_model=SalaResponse, status_code=status.HTTP_200_OK)
def get_sala(sala_id: Annotated[int, Path(ge=1)], db: Session = Depends(get_db)) -> SalaResponse:
    service = SalaService(db)
    return service.get_by_id(sala_id)


@router.post("", response_model=SalaResponse, status_code=status.HTTP_201_CREATED)
def create_sala(payload: SalaCreate, db: Session = Depends(get_db)) -> SalaResponse:
    service = SalaService(db)
    return service.create(payload)


@router.put("/{sala_id}", response_model=SalaResponse, status_code=status.HTTP_200_OK)
def update_sala(sala_id: Annotated[int, Path(ge=1)], payload: SalaUpdate, db: Session = Depends(get_db)) -> SalaResponse:
    service = SalaService(db)
    return service.update(sala_id, payload)


@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sala(sala_id: Annotated[int, Path(ge=1)], db: Session = Depends(get_db)) -> Response:
    service = SalaService(db)
    service.delete(sala_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
