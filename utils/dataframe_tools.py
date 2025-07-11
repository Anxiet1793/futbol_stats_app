# utils/dataframe_tools.py

import pandas as pd
from datetime import datetime

def mongo_to_dataframe(mongo_documents):
    """
    Convierte una lista de documentos de MongoDB a un Pandas DataFrame.
    Maneja el campo '_id' para que sea más amigable.
    """
    if not mongo_documents:
        return pd.DataFrame()

    df = pd.DataFrame(mongo_documents)

    # Convertir ObjectId a string para el campo '_id' si existe
    if '_id' in df.columns:
        df['_id'] = df['_id'].astype(str)

    # Convertir la columna 'fecha' a tipo datetime si existe
    if 'fecha' in df.columns:
        # Intenta convertir, si falla, deja como está o maneja el error
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

    return df

def dataframe_to_mongo(dataframe):
    """
    Convierte un Pandas DataFrame a una lista de diccionarios (documentos para MongoDB).
    """
    if dataframe.empty:
        return []

    # Si el DataFrame tiene una columna '_id' que era un string,
    # y necesitas convertirla de nuevo a ObjectId para operaciones de MongoDB,
    # lo harías aquí. Por simplicidad, la dejaremos como string.
    # Si vas a insertar nuevos documentos, asegúrate de no incluir un '_id' existente.

    # Convertir la columna 'fecha' de datetime a ISO string si existe
    if 'fecha' in dataframe.columns and pd.api.types.is_datetime64_any_dtype(dataframe['fecha']):
        dataframe['fecha'] = dataframe['fecha'].dt.isoformat() + 'Z'

    return dataframe.to_dict(orient='records')

def clean_and_format_dataframe(df):
    """
    Realiza una limpieza básica y formateo en el DataFrame.
    - Rellena valores nulos (NaN) con valores predeterminados.
    - Asegura tipos de datos correctos.
    """
    if df.empty:
        return df

    # Rellenar valores nulos para columnas numéricas
    numeric_cols = [
        'goles_local', 'goles_visitante', 'posesion_local', 'posesion_visitante',
        'tarjetas_amarillas_local', 'tarjetas_amarillas_visitante',
        'remates_local', 'remates_visitante', 'temporada'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Rellenar valores nulos para columnas de texto
    text_cols = ['equipo_local', 'equipo_visitante', 'liga']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Desconocido').astype(str)

    # Asegurar que 'es_local' sea booleano
    if 'es_local' in df.columns:
        df['es_local'] = df['es_local'].fillna(False).astype(bool)

    return df

# Ejemplo de uso (opcional, para pruebas)
if __name__ == "__main__":
    # Crear algunos documentos de MongoDB de ejemplo
    mongo_docs = [
        {
            "_id": "60c72b2f9b1e8b001c8e4d1a",
            "fixture_id": 100,
            "fecha": "2025-07-10T18:30:00Z",
            "equipo_local": "Real Madrid",
            "equipo_visitante": "Barcelona",
            "es_local": True,
            "goles_local": 2,
            "goles_visitante": 0,
            "posesion_local": 60,
            "posesion_visitante": 40,
            "tarjetas_amarillas_local": 1,
            "tarjetas_amarillas_visitante": 2,
            "remates_local": 15,
            "remates_visitante": 8,
            "liga": "La Liga",
            "temporada": 2025
        },
        {
            "_id": "60c72b2f9b1e8b001c8e4d1b",
            "fixture_id": 101,
            "fecha": "2025-07-09T15:00:00Z",
            "equipo_local": "Man Utd",
            "equipo_visitante": "Liverpool",
            "es_local": False,
            "goles_local": 1,
            "goles_visitante": 1,
            "posesion_local": 45,
            "posesion_visitante": 55,
            "tarjetas_amarillas_local": 3,
            "tarjetas_amarillas_visitante": 1,
            "remates_local": 10,
            "remates_visitante": 12,
            "liga": "Premier League",
            "temporada": 2025
        },
        {
            "_id": "60c72b2f9b1e8b001c8e4d1c",
            "fixture_id": 102,
            "fecha": "2025-07-08T21:00:00Z",
            "equipo_local": "Bayern Munich",
            "equipo_visitante": "Dortmund",
            "es_local": True,
            "goles_local": 3,
            "goles_visitante": 2,
            "posesion_local": 50,
            "posesion_visitante": 50,
            "tarjetas_amarillas_local": 0,
            "tarjetas_amarillas_visitante": 0,
            "remates_local": 18,
            "remates_visitante": 9,
            "liga": "Bundesliga",
            "temporada": 2025
        },
        # Documento con algunos valores nulos/faltantes para probar limpieza
        {
            "_id": "60c72b2f9b1e8b001c8e4d1d",
            "fixture_id": 103,
            "fecha": "2025-07-07T19:00:00Z",
            "equipo_local": "PSG",
            "equipo_visitante": "Marseille",
            "es_local": True,
            "goles_local": None, # Valor nulo
            "posesion_local": 70,
            "liga": "Ligue 1",
            "temporada": 2025
        }
    ]

    print("--- Convirtiendo documentos de Mongo a DataFrame ---")
    df = mongo_to_dataframe(mongo_docs)
    print(df.head())
    print("\nTipos de datos originales:")
    print(df.dtypes)

    print("\n--- Limpiando y formateando DataFrame ---")
    df_cleaned = clean_and_format_dataframe(df.copy())
    print(df_cleaned.head())
    print("\nTipos de datos después de la limpieza:")
    print(df_cleaned.dtypes)

    print("\n--- Convirtiendo DataFrame de vuelta a documentos de Mongo ---")
    mongo_docs_from_df = dataframe_to_mongo(df_cleaned)
    for doc in mongo_docs_from_df:
        print(doc)