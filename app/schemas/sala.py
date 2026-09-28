from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.sala import SalaEstado


def _normalize_string(value: str, field_name: str, *, minimum: int, maximum: int) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} no puede estar vacío.")
    if len(normalized) < minimum or len(normalized) > maximum:
        raise ValueError(f"{field_name} debe tener entre {minimum} y {maximum} caracteres.")
    return normalized


def _normalize_optional_description(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_equipment(items: list[str] | None) -> list[str]:
    if items is None:
        return []

    normalized_items: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = item.strip().lower()
        if not normalized:
            raise ValueError("El equipamiento no puede contener valores vacíos.")
        if normalized not in seen:
            seen.add(normalized)
            normalized_items.append(normalized)
    return normalized_items


class SalaCreate(BaseModel):
    nombre: str
    descripcion: str | None = Field(default=None, max_length=500)
    capacidad: int = Field(ge=1, le=1000)
    ubicacion: str
    equipamiento: list[str] = Field(default_factory=list)
    estado: SalaEstado = SalaEstado.disponible

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str) -> str:
        return _normalize_string(value, "El nombre", minimum=3, maximum=100)

    @field_validator("ubicacion")
    @classmethod
    def validate_ubicacion(cls, value: str) -> str:
        return _normalize_string(value, "La ubicación", minimum=2, maximum=150)

    @field_validator("descripcion")
    @classmethod
    def validate_descripcion(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_description(value)
        if normalized and len(normalized) > 500:
            raise ValueError("La descripción no puede superar los 500 caracteres.")
        return normalized

    @field_validator("equipamiento")
    @classmethod
    def validate_equipamiento(cls, value: list[str]) -> list[str]:
        return _normalize_equipment(value)


class SalaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = Field(default=None, max_length=500)
    capacidad: int | None = Field(default=None, ge=1, le=1000)
    ubicacion: str | None = None
    equipamiento: list[str] | None = None
    estado: SalaEstado | None = None

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_string(value, "El nombre", minimum=3, maximum=100)

    @field_validator("ubicacion")
    @classmethod
    def validate_ubicacion(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_string(value, "La ubicación", minimum=2, maximum=150)

    @field_validator("descripcion")
    @classmethod
    def validate_descripcion(cls, value: str | None) -> str | None:
        normalized = _normalize_optional_description(value)
        if normalized and len(normalized) > 500:
            raise ValueError("La descripción no puede superar los 500 caracteres.")
        return normalized

    @field_validator("equipamiento")
    @classmethod
    def validate_equipamiento(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return _normalize_equipment(value)


class SalaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    capacidad: int
    ubicacion: str
    equipamiento: list[str]
    estado: SalaEstado
    created_at: datetime
    updated_at: datetime
