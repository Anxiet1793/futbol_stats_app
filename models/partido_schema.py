# models/partido_schema.py

# Este módulo define la estructura esperada para un documento de partido en MongoDB.
# Se usa un diccionario simple para representar el esquema.
# Podrías usar Pydantic para una validación de datos más robusta si lo necesitas.

partido_schema = {
    "fixture_id": int,
    "fecha": str,  # Se almacenará como ISO string, luego se puede convertir a datetime
    "equipo_local": str,
    "equipo_visitante": str,
    "es_local": bool,
    "goles_local": int,
    "goles_visitante": int,
    "posesion_local": int,
    "posesion_visitante": int,
    "tarjetas_amarillas_local": int,
    "tarjetas_amarillas_visitante": int,
    "remates_local": int,
    "remates_visitante": int,
    "liga": str,
    "temporada": int
}

# Ejemplo de un documento de partido para referencia
ejemplo_partido = {
    "fixture_id": 1034502,
    "fecha": "2025-07-11T20:00:00Z",
    "equipo_local": "Chelsea",
    "equipo_visitante": "Arsenal",
    "es_local": True,
    "goles_local": 2,
    "goles_visitante": 1,
    "posesion_local": 54,
    "posesion_visitante": 46,
    "tarjetas_amarillas_local": 1,
    "tarjetas_amarillas_visitante": 3,
    "remates_local": 7,
    "remates_visitante": 11,
    "liga": "Premier League",
    "temporada": 2025
}