import requests
import pymongo

# Clave API proporcionada por API-Football
api_key = '834369634876ea331d8bf7d5b3de9639'  # Tu clave API

# URL base de la API-Football
base_url_fixtures = 'https://v3.football.api-sports.io/fixtures?date=2025-07-11'
base_url_statistics = 'https://api-football-v1.p.rapidapi.com/v3/statistics'

# Encabezados necesarios para la solicitud
headers = {
    'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com',
    'X-RapidAPI-Key': api_key  # Usar tu clave API aquí
}

# Parámetros para obtener partidos en vivo
params = {}

# Realizar la solicitud a la API para obtener los partidos en vivo
response = requests.get(base_url_fixtures, headers=headers, params=params)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    data = response.json()  # Parsear la respuesta JSON
    partidos = data.get('response', [])

    if partidos:
        # Conectar a MongoDB Atlas
        connection_string = "mongodb+srv://jfalconf:miContraseñaReal@futbolstats.cty7zbc.mongodb.net/?retryWrites=true&w=majority&appName=FutbolStats"
        client = pymongo.MongoClient(connection_string)

        # Seleccionar la base de datos y la colección
        db = client["futbol_db"]
        collection = db["partidos_en_vivo"]

        # Procesar los partidos obtenidos de la API y almacenarlos en MongoDB
        for partido in partidos:
            equipo_local = partido['teams']['home']['name']
            equipo_visitante = partido['teams']['away']['name']
            goles_local = partido['goals']['home']
            goles_visitante = partido['goals']['away']
            minuto = partido['fixture']['status']['elapsed']

            # Obtener estadísticas detalladas del partido
            partido_id = partido['fixture']['id']
            stats_response = requests.get(f"{base_url_statistics}/{partido_id}", headers=headers)

            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                stats = stats_data.get('response', [])

                if stats:
                    # Estadísticas adicionales
                    posesion_local = stats[0]['statistics'][0]['value']
                    posesion_visitante = stats[0]['statistics'][1]['value']
                    tarjetas_amarillas_local = stats[0]['statistics'][2]['value']
                    tarjetas_amarillas_visitante = stats[0]['statistics'][3]['value']
                    tiros_local = stats[0]['statistics'][4]['value']
                    tiros_visitante = stats[0]['statistics'][5]['value']

                    # Imprimir estadísticas detalladas del partido en vivo
                    print(f"Partido: {equipo_local} vs {equipo_visitante}")
                    print(f"Goles: {equipo_local} {goles_local} - {goles_visitante} {equipo_visitante}")
                    print(f"Minuto: {minuto} minutos jugados")
                    print(f"Posesión: {equipo_local} {posesion_local}% - {posesion_visitante}% {equipo_visitante}")
                    print(
                        f"Tarjetas Amarillas: {equipo_local} {tarjetas_amarillas_local} - {tarjetas_amarillas_visitante} {equipo_visitante}")
                    print(f"Tiros: {equipo_local} {tiros_local} - {tiros_visitante} {equipo_visitante}")
                    print("\n")

                    # Crear un documento con los datos del partido
                    partido_data = {
                        "equipo_local": equipo_local,
                        "equipo_visitante": equipo_visitante,
                        "goles_local": goles_local,
                        "goles_visitante": goles_visitante,
                        "minuto": minuto,
                        "posesion_local": posesion_local,
                        "posesion_visitante": posesion_visitante,
                        "tarjetas_amarillas_local": tarjetas_amarillas_local,
                        "tarjetas_amarillas_visitante": tarjetas_amarillas_visitante,
                        "tiros_local": tiros_local,
                        "tiros_visitante": tiros_visitante
                    }

                    # Insertar o actualizar los datos del partido en MongoDB
                    collection.update_one({"equipo_local": equipo_local, "equipo_visitante": equipo_visitante},
                                          {"$set": partido_data}, upsert=True)

        print("Datos insertados correctamente en MongoDB.")
    else:
        print("No hay partidos en vivo en este momento.")
else:
    print(f"Error al obtener datos: {response.status_code}")