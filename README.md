# CursoIA_Proy01

API backend para gestionar salas de reuniones con FastAPI y SQLAlchemy 2.x.

## Requisitos

- Python 3.12+
- Node.js 20+ (para las pruebas Playwright ya existentes)
- Opcional para SQL Server: ODBC Driver 18 for SQL Server

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm ci
```

## Configuración

1. Copia `/home/runner/work/CursoIA_Proy01/CursoIA_Proy01/.env.example` a `.env`.
2. Define `DATABASE_URL`.

Ejemplo SQLite para desarrollo:

```env
DATABASE_URL=sqlite:///./salas.db
```

Ejemplo SQL Server:

```env
DATABASE_URL=mssql+pyodbc://usuario@localhost:1433/CursoIA_Proy01?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&authentication=SqlPassword
```

## Ejecución

```bash
uvicorn app.main:app --reload
```

Swagger estará disponible en:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Semántica de borrado

`DELETE /api/salas/{id}` aplica una **baja lógica**: la sala pasa a estado `inactiva`.
Antes de hacerlo, el servicio consulta una abstracción de reservas futuras. Hoy se usa una implementación temporal (`NullReservationChecker`) porque el módulo de reservas todavía no existe.

## Migraciones y base de datos

El proyecto crea la tabla `salas` automáticamente al iniciar la aplicación mediante SQLAlchemy. No se ha añadido Alembic porque el repositorio no tenía infraestructura backend previa; la configuración actual queda preparada para incorporarlo en una siguiente iteración sin cambiar el modelo ni las capas.

## Pruebas

Pruebas Python:

```bash
pytest
```

Pruebas Playwright existentes:

```bash
npx playwright test
```

Las pruebas de API usan SQLite en memoria.

## Endpoints

- `GET /api/salas`
- `GET /api/salas/{sala_id}`
- `POST /api/salas`
- `PUT /api/salas/{sala_id}` (acepta actualización parcial)
- `DELETE /api/salas/{sala_id}` (baja lógica)

## Limitaciones actuales

- La comprobación real de reservas futuras está preparada mediante una abstracción, pero todavía no existe integración con un módulo de reservas.
- Para usar SQL Server es necesario disponer del driver ODBC adecuado en el entorno.
