import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from db.queries import insert_document, get_collection
from models.partido_schema import ejemplo_partido # Usamos el ejemplo como base

# Carga las variables de entorno para la API Key de API-Football
# Asegúrate de tener un archivo .env en la raíz de tu proyecto con:
# API_FOOTBALL_KEY="tu_api_key_aqui"
load_dotenv()

API_FOOTBALL_KEY = os.getenv("d9c8ef2a77d6cecfbe34b05f63811a03")
API_FOOTBALL_BASE_URL = "https://dashboard.api-football.com/profile?access"

def fetch_and_store_matches_from_api(date_str=None, league_id=None, season=None):
    """
    Función para consumir la API-Football y almacenar los datos en MongoDB.
    Esta es una implementación de ejemplo. Necesitarás ajustar los endpoints
    y la lógica de extracción según la documentación de API-Football.

    Args:
        date_str (str, optional): Fecha en formato 'YYYY-MM-DD' para filtrar partidos.
        league_id (int, optional): ID de la liga para filtrar.
        season (int, optional): Año de la temporada para filtrar.
    """
    if not API_FOOTBALL_KEY:
        print("Error: La variable de entorno API_FOOTBALL_KEY no está configurada.")
        return

    headers = {
        'x-rapidapi-key': API_FOOTBALL_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    # Ejemplo de endpoint para partidos (fixtures)
    # Consulta la documentación de API-Football para los parámetros correctos
    # https://www.api-football.com/documentation-v3
    endpoint = f"{API_FOOTBALL_BASE_URL}fixtures"
    params = {}
    if date_str:
        params['date'] = date_str
    if league_id:
        params['league'] = league_id
    if season:
        params['season'] = season

    print(f"Intentando obtener datos de: {endpoint} con parámetros: {params}")

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status() # Lanza una excepción para errores HTTP
        data = response.json()

        # Verifica si la respuesta contiene datos de partidos
        if data and 'response' in data and data['response']:
            print(f"Recibidos {len(data['response'])} partidos de la API.")
            for match_data in data['response']:
                # Aquí debes mapear la estructura de la respuesta de la API-Football
                # a tu `partido_schema`. Esto es crucial y específico de la API.
                # El siguiente es un ejemplo simplificado.

                # Ejemplo de cómo podrías extraer y transformar datos:
                # Asegúrate de que los campos existan en la respuesta de la API
                # y maneja los casos donde puedan faltar.
                processed_match = {
                    "fixture_id": match_data.get('fixture', {}).get('id'),
                    "fecha": match_data.get('fixture', {}).get('date'), # Ya debería ser ISO
                    "equipo_local": match_data.get('teams', {}).get('home', {}).get('name'),
                    "equipo_visitante": match_data.get('teams', {}).get('away', {}).get('name'),
                    "es_local": True, # Esto dependerá de cómo uses el dato, es un ejemplo
                    "goles_local": match_data.get('goals', {}).get('home'),
                    "goles_visitante": match_data.get('goals', {}).get('away'),
                    "posesion_local": match_data.get('statistics', [{}])[0].get('statistics', [{}])[0].get('value'), # Esto es muy simplificado, la posesión está anidada
                    "posesion_visitante": match_data.get('statistics', [{}])[1].get('statistics', [{}])[0].get('value'),
                    "tarjetas_amarillas_local": 0, # Placeholder, necesitarías buscar esto en las estadísticas
                    "tarjetas_amarillas_visitante": 0, # Placeholder
                    "remates_local": 0, # Placeholder
                    "remates_visitante": 0, # Placeholder
                    "liga": match_data.get('league', {}).get('name'),
                    "temporada": match_data.get('league', {}).get('season')
                }

                # Es importante validar y limpiar los datos antes de insertar
                # Por ejemplo, asegurarse de que los campos numéricos sean ints, etc.
                # Aquí se usa un ejemplo de documento para simular la inserción
                # En un caso real, usarías `processed_match`
                insert_document(processed_match) # Inserta el documento procesado
        else:
            print("No se encontraron partidos para los criterios especificados o la respuesta de la API está vacía.")

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API-Football: {e}")
    except ValueError as e:
        print(f"Error al parsear la respuesta JSON de la API: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado al obtener o procesar partidos: {e}")

def simulate_fetch_and_store_dummy_data(num_matches=5):
    """
    Simula la obtención de datos y los almacena en la base de datos.
    Útil para pruebas sin depender de la API-Football.
    """
    print(f"Simulando la obtención y almacenamiento de {num_matches} partidos de prueba...")
    for i in range(num_matches):
        dummy_match = ejemplo_partido.copy()
        dummy_match["fixture_id"] = dummy_match["fixture_id"] + i
        dummy_match["equipo_local"] = f"Equipo Local {i+1}"
        dummy_match["equipo_visitante"] = f"Equipo Visitante {i+1}"
        dummy_match["fecha"] = (datetime.now() - timedelta(days=i)).isoformat() + "Z"
        dummy_match["goles_local"] = i % 4
        dummy_match["goles_visitante"] = (i + 1) % 3
        dummy_match["liga"] = "Liga de Prueba" if i % 2 == 0 else "Otra Liga"
        dummy_match["temporada"] = 2025

        insert_document(dummy_match)
    print(f"Se insertaron {num_matches} partidos de prueba en MongoDB.")

# Ejemplo de uso (opcional, para pruebas)
if __name__ == "__main__":
    # Para probar la obtención de datos reales, descomenta la línea de abajo
    # y asegúrate de tener tu API_FOOTBALL_KEY configurada.
    # Fetch_and_store_matches_from_api(date_str="2024-07-10", league_id=39, season=2023) # Premier League, temporada 2023

    # Para simular datos de prueba sin la API
    simulate_fetch_and_store_dummy_data(num_matches=10)