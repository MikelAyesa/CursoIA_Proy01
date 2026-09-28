Característica: CRUD de salas de reuniones
  Como usuario de la API
  Quiero gestionar salas de reuniones
  Para consultar, crear, actualizar y desactivar salas de forma segura

  Escenario: Creación válida
    Dado que no existe una sala con nombre "Sala Norte"
    Cuando envío un POST a "/api/salas" con un nombre válido, capacidad positiva y ubicación válida
    Entonces la API responde 201
    Y devuelve la sala creada con el estado "disponible"

  Escenario: Nombre duplicado
    Dado que ya existe una sala con nombre "Sala Norte"
    Cuando envío un POST a "/api/salas" con el nombre "sala norte"
    Entonces la API responde 409
    Y devuelve el detalle "Ya existe una sala con ese nombre."

  Escenario: Listado y filtrado por estado
    Dado que existen salas en estado "disponible" y "mantenimiento"
    Cuando consulto "/api/salas?estado=disponible"
    Entonces la API responde 200
    Y devuelve únicamente salas en estado "disponible"

  Escenario: Consulta existente e inexistente
    Dado que existe una sala con identificador 1
    Cuando consulto "/api/salas/1"
    Entonces la API responde 200
    Pero si consulto "/api/salas/999"
    Entonces la API responde 404

  Escenario: Datos inválidos
    Cuando envío un POST a "/api/salas" con capacidad 0 o un estado inválido
    Entonces la API responde 422

  Escenario: Actualización válida
    Dado que existe una sala con identificador 1
    Cuando envío un PUT a "/api/salas/1" con una actualización parcial válida
    Entonces la API responde 200
    Y devuelve la sala actualizada

  Escenario: Actualización inexistente o con conflicto
    Dado que no existe una sala con identificador 999
    Cuando envío un PUT a "/api/salas/999"
    Entonces la API responde 404
    Y si intento renombrar una sala con un nombre ya existente
    Entonces la API responde 409

  Escenario: Eliminación válida
    Dado que existe una sala sin reservas futuras
    Cuando envío un DELETE a "/api/salas/1"
    Entonces la API responde 204
    Y la sala queda en estado "inactiva"

  Escenario: Eliminación bloqueada por reservas futuras
    Dado que existe una sala con reservas futuras
    Cuando envío un DELETE a "/api/salas/1"
    Entonces la API responde 409
    Y devuelve el detalle "No se puede eliminar la sala porque tiene reservas futuras."
