from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

_client: Client = None

def get_client() -> Client:
    """Retorna el cliente Supabase. Crea uno nuevo si no existe."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar definidos en .env")
        _client = create_client(url, key)
    return _client

def get(tabla: str, filtros: dict = None):
    """Lee registros de una tabla con filtros opcionales."""
    try:
        client = get_client()
        query = client.table(tabla).select("*")
        if filtros:
            for campo, valor in filtros.items():
                query = query.eq(campo, valor)
        return query.execute().data
    except Exception as e:
        print(f"[DB ERROR] get({tabla}): {e}")
        return []

def insert(tabla: str, datos: dict):
    """Inserta un registro en una tabla."""
    try:
        client = get_client()
        return client.table(tabla).insert(datos).execute().data
    except Exception as e:
        print(f"[DB ERROR] insert({tabla}): {e}")
        return None

def update(tabla: str, datos: dict, filtros: dict):
    """Actualiza registros en una tabla según filtros."""
    try:
        client = get_client()
        query = client.table(tabla).update(datos)
        for campo, valor in filtros.items():
            query = query.eq(campo, valor)
        return query.execute().data
    except Exception as e:
        print(f"[DB ERROR] update({tabla}): {e}")
        return None

def delete(tabla: str, filtros: dict):
    """Elimina registros de una tabla según filtros."""
    try:
        client = get_client()
        query = client.table(tabla).delete()
        for campo, valor in filtros.items():
            query = query.eq(campo, valor)
        return query.execute().data
    except Exception as e:
        print(f"[DB ERROR] delete({tabla}): {e}")
        return None
