import pandas as pd
from sqlmodel import Session, select
from sqlalchemy import text
from database import engine 
from models import (
    User, Arrendatario, Renta, HistorialRenta, 
    RentaMuebles, RentaServicios, CatalogoMuebles, 
    CatalogoServicios
)
from main import get_password_hash 
import numpy as np
import os
from typing import List

# --- FUNCIÓN PARA VACIAR TABLAS (CORREGIDA CON NOMBRES PEGADOS) ---
# --- FUNCIÓN PARA VACIAR TABLAS (CORREGIDA USANDO SNAKE_CASE) ---
# Asegúrate de que tienes "from sqlalchemy import text" al inicio.

def truncate_tables(session: Session):
    """Elimina todos los datos de las tablas en el orden correcto de dependencia,
    usando la convención de nombres snake_case (ej. renta_servicios)."""
    print("🗑️ Vaciando tablas existentes...")
    
    # 1. Tablas de enlace (primero): renta_servicios, renta_muebles
    # **CORRECCIÓN** (Usando snake_case consistente)
    session.exec(text("DELETE FROM renta_servicios"))
    session.exec(text("DELETE FROM renta_muebles"))
    
    # 2. Tablas dependientes: historial_renta
    # **CORRECCIÓN** (Usando snake_case para coincidir con el modelo HistorialRenta)
    session.exec(text("DELETE FROM historialrenta"))
    session.exec(text("DELETE FROM renta"))
    
    # 3. Catálogos y Arrendatario
    session.exec(text("DELETE FROM arrendatario"))
    session.exec(text("DELETE FROM catalogo_muebles"))
    session.exec(text("DELETE FROM catalogo_servicios"))
    
    # 4. Tabla User (al final)
    session.exec(text("DELETE FROM \"user\"")) 
    
    # Restablecer secuencias de IDs (snake_case)
    session.exec(text("ALTER SEQUENCE user_id_seq RESTART WITH 1"))
    session.exec(text("ALTER SEQUENCE arrendatario_id_seq RESTART WITH 1"))
    session.exec(text("ALTER SEQUENCE renta_id_seq RESTART WITH 1"))
    session.exec(text("ALTER SEQUENCE historialrenta_id_seq RESTART WITH 1"))
    session.exec(text("ALTER SEQUENCE renta_muebles_id_seq RESTART WITH 1"))
    session.exec(text("ALTER SEQUENCE renta_servicios_id_seq RESTART WITH 1"))
    session.exec(text("ALTER SEQUENCE catalogo_muebles_id_seq RESTART WITH 1"))
    session.exec(text("ALTER SEQUENCE catalogo_servicios_id_seq RESTART WITH 1"))
    
    session.commit()
    print("✅ Tablas vaciadas y secuencias reiniciadas.")
# ----------------------------------------
# ----------------------------------------

# Rutas a los archivos CSV generados
CSV_PATHS = {
    "arrendatarios": "arrendatarios.csv",
    "rentas": "rentas.csv",
    "historialrenta": "historial_renta.csv",
    "renta_muebles": "renta_muebles.csv",
    "renta_servicios": "renta_servicios.csv",
    # Asume que estos catálogos existen
    "catalogo_muebles": "catalogo_muebles.csv", 
    "catalogo_servicios": "catalogo_servicios.csv",
}

# Mapeo de modelos a DataFrames
MODEL_MAP = {
    Arrendatario: "arrendatarios",
    Renta: "rentas",
    HistorialRenta: "historialrenta",
    RentaMuebles: "renta_muebles",
    RentaServicios: "renta_servicios",
    CatalogoMuebles: "catalogo_muebles",
    CatalogoServicios: "catalogo_servicios",
}


def load_data_from_csv(file_key: str) -> pd.DataFrame:
    """Carga un CSV asegurando que existe."""
    path = CSV_PATHS.get(file_key)
    if not path or not os.path.exists(path):
        print(f"❌ Error: El archivo CSV para '{file_key}' no se encontró en '{path}'.")
        return None
    return pd.read_csv(path)

def create_users_from_arrendatarios(df_arrendatarios: pd.DataFrame, session: Session) -> List[User]:
    """
    Crea un objeto User por cada Arrendatario, generando un username y password.
    
    El username será una versión limpia del nombre, el password será fijo (e.g., '123').
    """
    new_users = []
    
    # 1. Crear data para Users
    df_arrendatarios['base_username'] = df_arrendatarios['nombre'].apply(
        lambda x: x.lower().replace(' ', '').replace('.', '').replace(',', '')
    )
    
    # Generar usernames únicos
    usernames = {}
    for index, row in df_arrendatarios.iterrows():
        base = row['base_username']
        # Limita el username a 12 caracteres y añade el ID para asegurar unicidad
        username = base[:12] + str(row['id']) 
        usernames[row['id']] = username 

    # 2. Insertar Users
    for arrendatario_id, username in usernames.items():
        # Evitar crear si el super_user inicial ya se llama 'admin'
        if username == "admin": 
            continue 

        # Crear User y hashear password
        new_user = User(
            username=username,
            password=get_password_hash("123"), # Contraseña fija para simulación
            role="arrendatario", 
            active=bool(df_arrendatarios.loc[df_arrendatarios['id'] == arrendatario_id, 'activo'].iloc[0]),
        )
        session.add(new_user)
        new_users.append(new_user)

    session.commit()
    # 3. Mapear los IDs de User
    # Después del commit, el objeto new_user tiene su ID asignado por la BDD.
    # Necesitamos un mapeo entre el ID *del CSV* y el ID *de la BDD*.
    
    # Re-obtener los users para asegurar que tenemos los IDs de la BDD
    users_in_db = session.exec(select(User).where(User.role == "arrendatario")).all()
    
    # Crear un diccionario para mapear el Arrendatario.nombre al User.id
    name_to_user_id = {user.username: user.id for user in users_in_db}
    
    # Este es el mapeo que importa: Arrendatario_ID_CSV -> User_ID_DB
    arrendatario_id_to_user_id = {}
    for user in users_in_db:
        # Intentar encontrar el Arrendatario_ID_CSV por el username
        # Esto es un poco hacky, pero funciona para mock data
        user_id_from_username = user.username.split('_')[-1]
        for index, row in df_arrendatarios.iterrows():
            if row['base_username'][:12] + str(row['id']) == user.username:
                arrendatario_id_to_user_id[row['id']] = user.id
                break

    # Reemplazar la columna 'user_id' en el DataFrame de arrendatarios
    # Para vincularlo al ID de User real.
    df_arrendatarios['user_id'] = df_arrendatarios['id'].apply(
        lambda x: arrendatario_id_to_user_id.get(x)
    )
    
    # Eliminar la columna de 'id' original para que SQLModel use la autogenerada
    # y conservar solo las columnas del modelo Arrendatario.
    df_arrendatarios = df_arrendatarios.rename(columns={'id': 'id_csv'})
    
    return df_arrendatarios


# ...
def fill_database():
    """Función principal para llenar todas las tablas."""
    
    print("--- 🛠️ Iniciando carga masiva de datos ---")

    try:
        with Session(engine) as session:
            
            # --- LLAMADA A LA FUNCIÓN DE VACIADO ---
            truncate_tables(session)
            # --------------------------------------

            # --- 1. Cargar Catálogos (Tablas simples) ---
            print("Cargando Catálogos...")
            for model, file_key in [(CatalogoMuebles, "catalogo_muebles"), (CatalogoServicios, "catalogo_servicios")]:
                df = load_data_from_csv(file_key)
                if df is not None and not df.empty:
                    # Eliminar la columna 'id' para que la BDD use su propia secuencia
                    df = df.drop(columns=['id'], errors='ignore')
                    data = df.to_dict('records')
                    session.add_all([model(**item) for item in data])
                print(f"✅ Catálogo '{model.__name__}' cargado.")


            # --- 2. Crear Users (Necesario antes de Arrendatarios) ---
            print("Creando usuarios y preparando arrendatarios...")
            df_arrendatarios = load_data_from_csv("arrendatarios")
            if df_arrendatarios is not None and not df_arrendatarios.empty:
                # Esta función crea los Users y modifica el DF de Arrendatarios 
                # para que tenga el user_id de la BDD.
                df_arrendatarios_for_db = create_users_from_arrendatarios(df_arrendatarios, session)
                
                
                # --- 3. Cargar Arrendatarios ---
                
                print("Cargando Arrendatarios...")
                # ...
                
                # ** ESTO DEBE ESTAR PRESENTE Y CORREGIDO **
                df_arrendatarios_for_db['telefono'] = df_arrendatarios_for_db['telefono'].astype(str)
                df_arrendatarios_for_db['correo'] = df_arrendatarios_for_db['correo'].astype(str).replace('<NA>', None)
                df_arrendatarios_for_db['correo'] = df_arrendatarios_for_db['correo'].replace('nan', None)
                # ------------------------------------------

                data_arrendatarios = df_arrendatarios_for_db.to_dict('records')
                session.add_all([Arrendatario(**item) for item in data_arrendatarios])
                session.commit() 
                print("✅ Arrendatarios y sus Users creados correctamente.")

            # --- 4. Cargar Rentas ---
            print("Cargando Rentas...")
            df_rentas = load_data_from_csv("rentas")
            if df_rentas is not None and not df_rentas.empty:
                # El id del arrendatario en el CSV es el ID de la tabla Arrendatario que acabamos de llenar
                # (ya que se mantuvo el orden). Si la BDD hubiera estado vacía, estos IDs coincidirían.
                
                # Simplificamos asumiendo que el 'arrendatario_id' en el CSV es secuencial y correcto
                # dado que lo creaste a partir de 1 hasta el número de arrendatarios.
                
                df_rentas = df_rentas.drop(columns=['id', 'oferta', 'fuente'], errors='ignore')
                
                # Renombrar columnas para que coincidan con el modelo
                df_rentas = df_rentas.rename(columns={
                    'edificio': 'edificio',
                    'banos': 'banos',
                    'habitaciones': 'habitaciones',
                    'lat': 'lat',
                    'lon': 'lon',
                    'mascotas': 'mascotas',
                    'tinaco': 'tinaco',
                    'estacionamiento': 'estacionamiento',
                    'activo': 'activo',
                    'disponible': 'disponible',
                    'precio': 'precio',
                    'arrendatario_id': 'arrendatario_id',
                })

                data_rentas = df_rentas.to_dict('records')
                session.add_all([Renta(**item) for item in data_rentas])
                session.commit()
                print("✅ Rentas cargadas correctamente.")
                
                # Obtener la lista de los IDs de renta reales de la BDD
                renta_ids_db = session.exec(select(Renta.id)).all()
            
            # --- 5. Cargar Historial de Rentas ---
            print("Cargando Historial de Rentas...")
            df_historial = load_data_from_csv("historialrenta")
            if df_historial is not None and not df_historial.empty and renta_ids_db:
                df_historial = df_historial.drop(columns=['id'], errors='ignore')
                
                # Mapear el ID de renta del CSV al ID real de la BDD.
                # Como los IDs de renta de BDD son secuenciales (1, 2, 3...) y
                # el CSV también usa secuenciales, podemos simplemente usar el índice.
                
                # Mapeo simple: renta_id_csv -> renta_id_db
                id_map = {i + 1: renta_ids_db[i] for i, _ in enumerate(renta_ids_db)}
                df_historial['renta_id'] = df_historial['renta_id'].map(id_map)
                
                # Asegurar que el formato de fecha es correcto
                df_historial['fecha_inicio'] = pd.to_datetime(df_historial['fecha_inicio']).dt.date
                df_historial['fecha_fin'] = pd.to_datetime(df_historial['fecha_fin']).dt.date

                data_historial = df_historial.to_dict('records')
                session.add_all([HistorialRenta(**item) for item in data_historial])
                session.commit()
                print("✅ Historial de Rentas cargado.")

            # --- 6. Cargar Renta Muebles y Renta Servicios (Tablas de enlace) ---
            print("Cargando tablas de enlace (Renta Muebles y Servicios)...")
            for model, file_key in [(RentaMuebles, "renta_muebles"), (RentaServicios, "renta_servicios")]:
                df = load_data_from_csv(file_key)
                if df is not None and not df.empty and renta_ids_db:
                    df = df.drop(columns=['id'], errors='ignore')
                    
                    # Mapear el ID de renta del CSV al ID real de la BDD
                    df['renta_id'] = df['renta_id'].map(id_map)
                    
                    data = df.to_dict('records')
                    session.add_all([model(**item) for item in data])
                print(f"✅ Tabla de enlace '{model.__name__}' cargada.")

            session.commit()
            print("\n🎉 Todos los datos han sido cargados exitosamente.")

    except Exception as e:
        print(f"\nFATAL ERROR durante la carga de datos: {e}")
        # La session se cerrará y hará un rollback automáticamente si ocurre un error


if __name__ == "__main__":
    # Asegúrate de que tus archivos CSV están en el mismo directorio
    # y que la función create_db_and_tables() ya fue ejecutada (por main.py)
    fill_database()