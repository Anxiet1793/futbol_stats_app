# db/mongo_config.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Carga las variables de entorno desde un archivo .env
# Asegúrate de tener un archivo .env en la raíz de tu proyecto con:
# MONGO_URI="mongodb+srv://<tu_usuario>:<tu_contraseña>@<tu_cluster>.mongodb.net/?retryWrites=true&w=majority"
# DB_NAME="futbol_db"
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "futbol_db") # Nombre de la base de datos, por defecto 'futbol_db'

client = None
db = None

def connect_to_mongodb():
    """
    Establece la conexión con MongoDB Atlas.
    Retorna el objeto de la base de datos si la conexión es exitosa, None en caso contrario.
    """
    global client, db
    if client and db:
        print("Ya conectado a MongoDB.")
        return db

    if not MONGO_URI:
        print("Error: La variable de entorno MONGO_URI no está configurada.")
        return None

    try:
        client = MongoClient(MONGO_URI)
        # El comando ping se usa para confirmar que la conexión es exitosa
        client.admin.command('ping')
        db = client[DB_NAME]
        print(f"Conexión exitosa a MongoDB Atlas, base de datos: {DB_NAME}")
        return db
    except ConnectionFailure as e:
        print(f"Error de conexión a MongoDB Atlas: {e}")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado al conectar a MongoDB: {e}")
        return None

def close_mongodb_connection():
    """Cierra la conexión con MongoDB."""
    global client, db
    if client:
        client.close()
        print("Conexión a MongoDB cerrada.")
        client = None
        db = None

# Ejemplo de uso (opcional, para pruebas)
if __name__ == "__main__":
    # Para probar la conexión, asegúrate de tener MONGO_URI en tu .env
    database = connect_to_mongodb()
    if database:
        print(f"Colecciones disponibles: {database.list_collection_names()}")
    close_mongodb_connection()