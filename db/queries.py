# db/queries.py

from bson.objectid import ObjectId
from db.mongo_config import connect_to_mongodb

# Obtiene la instancia de la base de datos
db = connect_to_mongodb()

# Verifica que la conexión se haya establecido correctamente
if not db:
    print("Error: No se pudo conectar a la base de datos. Las operaciones de la DB no funcionarán.")

def get_collection(collection_name="partidos"):
    """
    Retorna la colección especificada.
    """
    if db:
        return db[collection_name]
    return None

def insert_document(document, collection_name="partidos"):
    """
    Inserta un solo documento en la colección especificada.
    Retorna el ID del documento insertado.
    """
    collection = get_collection(collection_name)
    if collection:
        try:
            result = collection.insert_one(document)
            print(f"Documento insertado con ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"Error al insertar documento: {e}")
            return None
    return None

def find_documents(query=None, collection_name="partidos"):
    """
    Encuentra documentos en la colección especificada que coincidan con la consulta.
    Si la consulta es None, retorna todos los documentos.
    Retorna una lista de documentos.
    """
    collection = get_collection(collection_name)
    if collection:
        try:
            if query is None:
                query = {}
            documents = list(collection.find(query))
            print(f"Encontrados {len(documents)} documentos.")
            return documents
        except Exception as e:
            print(f"Error al buscar documentos: {e}")
            return []
    return []

def update_document(document_id, updates, collection_name="partidos"):
    """
    Actualiza un documento específico por su ID.
    `document_id` puede ser una cadena (para ObjectId) o un ObjectId.
    `updates` es un diccionario con los campos a actualizar.
    Retorna True si la actualización fue exitosa, False en caso contrario.
    """
    collection = get_collection(collection_name)
    if collection:
        try:
            # Asegura que el ID sea un ObjectId
            if isinstance(document_id, str):
                document_id = ObjectId(document_id)

            result = collection.update_one({"_id": document_id}, {"$set": updates})
            if result.matched_count > 0:
                print(f"Documento con ID {document_id} actualizado. Modificados: {result.modified_count}")
                return True
            else:
                print(f"No se encontró documento con ID {document_id} para actualizar.")
                return False
        except Exception as e:
            print(f"Error al actualizar documento con ID {document_id}: {e}")
            return False
    return False

def delete_document(document_id, collection_name="partidos"):
    """
    Elimina un documento específico por su ID.
    `document_id` puede ser una cadena (para ObjectId) o un ObjectId.
    Retorna True si la eliminación fue exitosa, False en caso contrario.
    """
    collection = get_collection(collection_name)
    if collection:
        try:
            # Asegura que el ID sea un ObjectId
            if isinstance(document_id, str):
                document_id = ObjectId(document_id)

            result = collection.delete_one({"_id": document_id})
            if result.deleted_count > 0:
                print(f"Documento con ID {document_id} eliminado.")
                return True
            else:
                print(f"No se encontró documento con ID {document_id} para eliminar.")
                return False
        except Exception as e:
            print(f"Error al eliminar documento con ID {document_id}: {e}")
            return False
    return False

# Funciones de filtrado específicas
def filter_by_date_range(start_date, end_date, collection_name="partidos"):
    """
    Filtra partidos por un rango de fechas.
    Las fechas deben estar en formato ISO 8601 (ej. "2025-07-01T00:00:00Z").
    """
    query = {
        "fecha": {
            "$gte": start_date,
            "$lte": end_date
        }
    }
    return find_documents(query, collection_name)

def filter_by_team(team_name, collection_name="partidos"):
    """
    Filtra partidos donde el equipo local o visitante coincide con el nombre del equipo.
    """
    query = {
        "$or": [
            {"equipo_local": team_name},
            {"equipo_visitante": team_name}
        ]
    }
    return find_documents(query, collection_name)

def get_unique_teams(collection_name="partidos"):
    """
    Obtiene una lista de todos los equipos únicos (locales y visitantes) en la colección.
    """
    collection = get_collection(collection_name)
    if collection:
        try:
            local_teams = collection.distinct("equipo_local")
            visitor_teams = collection.distinct("equipo_visitante")
            all_teams = sorted(list(set(local_teams + visitor_teams)))
            return all_teams
        except Exception as e:
            print(f"Error al obtener equipos únicos: {e}")
            return []
    return []

def get_unique_leagues(collection_name="partidos"):
    """
    Obtiene una lista de todas las ligas únicas en la colección.
    """
    collection = get_collection(collection_name)
    if collection:
        try:
            leagues = collection.distinct("liga")
            return sorted(leagues)
        except Exception as e:
            print(f"Error al obtener ligas únicas: {e}")
            return []
    return []

# Ejemplo de uso (opcional, para pruebas)
if __name__ == "__main__":
    # Asegúrate de tener documentos en tu colección 'partidos' para probar
    # Puedes usar el script fetch_matches.py para insertar algunos datos de prueba.

    # Insertar un documento de prueba
    from models.partido_schema import ejemplo_partido
    print("\n--- Probando inserción ---")
    inserted_id = insert_document(ejemplo_partido)

    # Buscar todos los documentos
    print("\n--- Probando búsqueda de todos los documentos ---")
    all_matches = find_documents()
    for match in all_matches[:3]: # Muestra solo los primeros 3
        print(match)

    # Buscar por un equipo específico (ej. "Chelsea")
    print("\n--- Probando búsqueda por equipo (Chelsea) ---")
    chelsea_matches = filter_by_team("Chelsea")
    for match in chelsea_matches[:3]:
        print(match)

    # Actualizar un documento (si se insertó uno)
    if inserted_id:
        print(f"\n--- Probando actualización del documento con ID: {inserted_id} ---")
        update_success = update_document(inserted_id, {"goles_local": 3, "posesion_local": 60})
        if update_success:
            updated_doc = find_documents({"_id": inserted_id})
            print(f"Documento actualizado: {updated_doc}")

    # Eliminar un documento (si se insertó uno)
    if inserted_id:
        print(f"\n--- Probando eliminación del documento con ID: {inserted_id} ---")
        delete_success = delete_document(inserted_id)
        print(f"Eliminación exitosa: {delete_success}")

    # Obtener equipos únicos
    print("\n--- Probando obtener equipos únicos ---")
    teams = get_unique_teams()
    print(f"Equipos únicos: {teams}")

    # Obtener ligas únicas
    print("\n--- Probando obtener ligas únicas ---")
    leagues = get_unique_leagues()
    print(f"Ligas únicas: {leagues}")
