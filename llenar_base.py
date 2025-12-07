import pandas as pd
import numpy as np
import time
import random
import requests
from bs4 import BeautifulSoup
import re
import json
from tqdm import tqdm
from unidecode import unidecode
import unicodedata
from datetime import datetime, timedelta
import os
from typing import List
from sqlmodel import Session, select
# --- Importación de SQLAlchemy necesaria para la conexión ---
import sqlalchemy
from sqlalchemy import text, create_engine


# --- 1. Catálogos en Memoria (Reemplazo de CSV) ---
CATALOGOS = {
    "servicios": pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6],
        'servicio': ['Luz', 'Agua', 'Internet', 'Gas', 'Telefono', 'Television por cable']
    }),
    "muebles": pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9],
        'mueble': ['Refrigerador', 'Estufa', 'Lavadora', 'Secadora', 'Cama', 'Sofá', 'Microondas', 'Televisión', 'Licuadora']
    })
}

# --- 2. Funciones de Limpieza y Extracción ---

def limpia_texto(text):
    if text is None:
        return ""
    cleaned_text = re.sub(r'[^\w\s.]', '', text).strip()
    cleaned_text = unidecode(cleaned_text.lower())
    return cleaned_text

def limpia_moneda(text):
    if text is None:
        return ""
    cleaned_coin = re.sub(r'[$,\n]', '', text).strip()
    return cleaned_coin

def limpia_datos(df):
    df = df.reset_index(drop=True)
    df = df[(df['precio'] > 0) & (df['precio'].notna())]
    df = df[~df['oferta'].str.contains('terreno|remodelar|hectareas')]
    df = df.drop_duplicates(subset=['oferta', 'precio', 'recamaras', 'bathrooms'], keep='first')
    df['precio_m2'] = df['precio'] / df['mts']
    return df

def quitar_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

# --- 3. Función de Web Scraping (icasas) ---

# NOTA: Asegúrate de que la variable 'headers' esté definida antes de llamar a icasas.
# La definiremos en el bloque principal.

def icasas(estado, tipo="renta"):
    if tipo == "venta":
        base_url = "https://www.icasas.mx/venta/habitacionales-casas-{}-2_5_3_0_11_0/t_departamentos/p_{}"
    elif tipo == "renta":
        base_url = "https://www.icasas.mx/renta/habitacionales-casas-{}-2_5_3_0_11_0/t_departamentos/p_{}"
    else:
        raise ValueError("Tipo de propiedad no válido. Usa 'venta' o 'renta'.")
        
    all_data = pd.DataFrame()
    for paginas in tqdm(range(1, 101), desc=f"Scrapeando icasas en {estado}"):
        url = base_url.format(estado, paginas)
        # La variable 'headers' debe estar accesible globalmente o como parámetro
        r = requests.get(url, headers=headers) 
        soup = BeautifulSoup(r.text, 'html.parser')
        resultados = soup.find_all('li', class_='serp-snippet ad featured')
        
        data = {
            'oferta': [], 'precio': [], 'mts': [], 
            'recamaras': [], 'bathrooms': [], 'lat': [], 'lon': []
        }
        
        for i in resultados:
            a_tag = i.find('a', class_='detail-redirection')
            data['oferta'].append(a_tag.get_text(strip=True) if a_tag else None)
            data['mts'].append(i.find('span', class_='areaBuilt').get_text(strip=True) if i.find('span', class_='areaBuilt') else None)
            data['recamaras'].append(i.find('span', class_='rooms').get_text(strip=True) if i.find('span', class_='rooms') else None)
            data['bathrooms'].append(i.find('span', class_='bathrooms').get_text(strip=True) if i.find('span', class_='bathrooms') else None)
            data['lat'].append(i.find('meta', itemprop='latitude')['content'] if i.find('meta', itemprop='latitude') else None)
            data['lon'].append(i.find('meta', itemprop='longitude')['content'] if i.find('meta', itemprop='longitude') else None)
            data['precio'].append(i.find('div', class_='price').get_text(strip=True) if i.find('div', class_='price') else None)

        temp = pd.DataFrame(data)
        all_data = pd.concat([all_data, temp], ignore_index=True)

    all_data["fecha_consulta"] = pd.to_datetime("today")
    all_data["fuente"] = "icasas"
    all_data["oferta"] = all_data["oferta"].apply(limpia_texto)
    all_data["precio"] = all_data["precio"].apply(limpia_moneda)
    all_data["precio"] = pd.to_numeric(all_data["precio"].str.extract(r'(\d+(?:\.\d+)?)')[0], errors="coerce")
    all_data["mts"] = pd.to_numeric(all_data["mts"].astype(str).str.extract(r'(\d+)')[0], errors="coerce")
    all_data["mts"] = all_data["mts"].astype(float)
    all_data["precio"] = all_data["precio"].astype(float)

    return all_data

# --- 4. Función de Simulación de Arrendatarios (Sin cambios) ---

def generar_arrendatarios(n=10):
    nombres = [
        "Carlos", "María", "José", "Ana", "Luis", "Laura", "Miguel", "Sofía", "Jorge", "Fernanda",
        "Andrés", "Patricia", "Ricardo", "Lucía", "Héctor", "Diana", "Sergio", "Camila", "Raúl", "Valeria", "Zarif",
        "Marlon", "Jazmín"
    ]
    apellidos = [
        "Hernández", "García", "Martínez", "López", "González", "Rodríguez", "Pérez", "Sánchez", "Ramírez", "Flores",
        "Torres", "Díaz", "Vargas", "Cruz", "Morales", "Gómez", "Castro", "Rojas", "Ruiz", "Jiménez", "León", "Jaramillo"
    ]

    arrendatarios = []
    for i in range(1, n + 1):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        nombre_completo = f"{nombre} {apellido}"
        telefono = "646" + "".join(str(random.randint(0, 9)) for _ in range(7))

        if random.random() < 0.7:
            nombre_sin_acentos = quitar_acentos(nombre.lower())
            apellido_sin_acentos = quitar_acentos(apellido.lower())
            numero_extra = random.randint(1, 9999)
            correo = f"{nombre_sin_acentos}.{apellido_sin_acentos}{numero_extra}@gmail.com"
        else:
            correo = None

        arrendatarios.append({
            "id": i,
            "nombre": nombre_completo,
            "telefono": telefono,
            "correo": correo,
            "activo": np.random.choice([True, False], p=[0.9, 0.1])
        })
        
    df = pd.DataFrame(arrendatarios)
    return df[['id', 'nombre', 'telefono', 'correo', 'activo']]


# --- 5. Función Principal de Generación (Sin cambios funcionales mayores) ---

def scrapear_y_simular(estado="baja-california-ensenada", tipo="renta", num_arrendatarios=85):
    
    print("🚀 Iniciando Web Scraping y Simulación...")

    # A. Scrapeo y Limpieza Inicial de Viviendas (Renta)
    vivi_renta = icasas(estado, tipo)
    
    # --- Limpieza de recamaras antes de la limpieza general ---
    vivi_renta["recamaras"] = vivi_renta["recamaras"].astype(str).str.extract(r'(\d+)')
    vivi_renta["recamaras"] = pd.to_numeric(vivi_renta["recamaras"], errors="coerce").astype('Int64')
    # ---------------------------------------------------------
    
    vivi_limpia_renta = vivi_renta.copy()
    vivi_limpia_renta = vivi_limpia_renta[~vivi_limpia_renta["oferta"].str.contains("lote|terreno|renta")]
    vivi_limpia_renta = vivi_limpia_renta[vivi_limpia_renta['lat'].notna()]
    vivi_limpia_renta = limpia_datos(vivi_limpia_renta)
    vivi_limpia_renta['precio'] = vivi_limpia_renta['precio'].round(0).astype(int)

    # B. Generar Arrendatarios
    arrendatarios_df = generar_arrendatarios(n=num_arrendatarios)
    print(f"✅ Generados {len(arrendatarios_df)} arrendatarios.")
    
    # C. Simulación de Renta Inmuebles
    renta = vivi_limpia_renta.copy()
    renta['Edificio'] = np.random.choice(['Casa', 'Departamento'], size=len(renta))
    
    renta['Banos'] = renta['recamaras'].apply(lambda x: 1 if x <= 2 else np.random.choice([1, 2]))

    renta['Mascotas'] = np.random.choice([True, False], size=len(renta))
    renta['Tinaco'] = np.random.choice([True, False], size=len(renta))
    renta['Estacionamiento'] = np.random.choice([0, 1], size=len(renta))
    renta['Activo'] = np.random.choice([True, False], size=len(renta), p=[0.9, 0.1])
    renta['Disponible'] = np.random.choice([True, False], size=len(renta), p=[0.8, 0.2])
    renta = renta.drop(columns=['mts', 'bathrooms', 'fecha_consulta', 'precio_m2', 'oferta', 'fuente'])
    
    n_filas = len(renta)
    numeros = np.arange(1, num_arrendatarios + 1)
    if n_filas > num_arrendatarios:
        numeros = np.concatenate([numeros, np.random.choice(numeros, size=n_filas - num_arrendatarios, replace=True)])
    np.random.shuffle(numeros)
    renta['arrendatario_id'] = numeros
    
    renta = renta.rename(columns={"recamaras": "habitaciones"}, errors="raise")
    renta['id'] = renta.index + 1
    renta.columns = [col.lower() for col in renta.columns]
    renta = renta[[
        'id', 'edificio', 'habitaciones', 'banos', 'lat', 'lon', 'mascotas',
        'tinaco', 'estacionamiento', 'activo', 'disponible', 'precio', 'arrendatario_id'
    ]]
    print(f"✅ Generadas {len(renta)} rentas.")
    
    # D. Simulación de Renta Muebles
    renta_muebles_filas = []
    catalogo_muebles_ids = CATALOGOS['muebles']['id'].tolist()
    for renta_id in renta['id']:
        num_muebles = random.randint(0, len(catalogo_muebles_ids))
        if num_muebles > 0:
            muebles_seleccionados = random.sample(catalogo_muebles_ids, k=num_muebles)
            for mueble_id in muebles_seleccionados:
                renta_muebles_filas.append({'renta_id': renta_id, 'mueble_id': mueble_id})
                
    renta_muebles = pd.DataFrame(renta_muebles_filas)
    renta_muebles.insert(0, 'id', range(1, len(renta_muebles) + 1))
    print(f"✅ Generados {len(renta_muebles)} registros de renta_muebles.")

    # E. Simulación de Renta Servicios
    renta_servicios_filas = []
    catalogo_servicios_ids = CATALOGOS['servicios']['id'].tolist()
    for renta_id in renta['id']:
        num_servicios = random.randint(0, len(catalogo_servicios_ids))
        if num_servicios > 0:
            servicios_seleccionados = random.sample(catalogo_servicios_ids, k=num_servicios)
            for servicio_id in servicios_seleccionados:
                renta_servicios_filas.append({'renta_id': renta_id, 'servicio_id': servicio_id})
                
    renta_servicios = pd.DataFrame(renta_servicios_filas)
    renta_servicios.insert(0, 'id', range(1, len(renta_servicios) + 1))
    renta_servicios['servicio_id'] = renta_servicios['servicio_id'].astype(int)
    print(f"✅ Generados {len(renta_servicios)} registros de renta_servicios.")

    # F. Simulación de Historial de Renta
    historial_filas = []
    precio_min = 5000
    precio_max = 25000
    for renta_id in renta['id'].tolist():
        num_periodos = random.randint(1, 3)
        inicio_primera_renta = datetime.today() - timedelta(days=random.randint(30, 3*365))
        precio_anterior = random.randint(precio_min, precio_max)
        
        for _ in range(num_periodos):
            duracion = timedelta(days=random.randint(60, 180))
            fecha_inicio = inicio_primera_renta
            fecha_fin = fecha_inicio + duracion
            
            variacion = random.uniform(-0.3, 0.3)
            precio = int(precio_anterior * (1 + variacion))
            precio_anterior = precio
            
            historial_filas.append({
                'renta_id': renta_id,
                'fecha_inicio': fecha_inicio.date(),
                'fecha_fin': fecha_fin.date(),
                'precio': precio
            })
            inicio_primera_renta = fecha_fin + timedelta(days=1)
            
    historial_renta = pd.DataFrame(historial_filas)
    historial_renta.insert(0, 'id', range(1, len(historial_renta) + 1))
    print(f"✅ Generados {len(historial_renta)} registros de historial.")
    
    print("--- Simulación completa en memoria ---")
    
    return {
        "arrendatarios": arrendatarios_df,
        "rentas": renta,
        # Renombrar 'historialrenta' para la consistencia en el código
        "historial_renta": historial_renta, 
        "renta_muebles": renta_muebles,
        "renta_servicios": renta_servicios,
        "catalogo_muebles": CATALOGOS['muebles'],
        "catalogo_servicios": CATALOGOS['servicios'],
    }


# ==============================================================================
# --- 6. Funcionalidad de Base de Datos ---
# ==============================================================================

# ⚠️ CONFIGURACIÓN DE CONEXIÓN
# Ajusta 'DB_USER', 'DB_HOST', y 'DB_PORT' si no usas los valores por defecto.
DB_USER = "postgres" 
DB_PASS = "Hey!Jaz26:)" # Contraseña proporcionada por el usuario
DB_HOST = "localhost" 
DB_PORT = "5432" 
DB_NAME = "rentasInmuebles_ensenada"

# Cadena de conexión de PostgreSQL con driver psycopg2
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def insertar_a_postgres(df: pd.DataFrame, table_name: str, engine: sqlalchemy.engine.Engine):
    """Inserta un DataFrame en una tabla de PostgreSQL y resetea la secuencia SERIAL."""
    print(f"-> Insertando datos en la tabla '{table_name}'...")
    try:
        # Usamos if_exists='append' para agregar datos a las tablas existentes.
        # ADVERTENCIA: Si deseas borrar los datos anteriores, usa if_exists='replace'.
        df.to_sql(
            table_name,
            engine,
            if_exists='append', 
            index=False,
            chunksize=1000,
            method='multi'
        )
        
        # Después de la inserción, es crucial resetear la secuencia SERIAL
        # de PostgreSQL para que los nuevos registros (ej: los insertados desde pgAdmin) 
        # no colisionen con los IDs insertados masivamente.
        with engine.begin() as connection:
            # Obtiene el ID máximo de la tabla y ajusta la secuencia (solo si la tabla tiene columna 'id')
            if 'id' in df.columns:
                 # El nombre de la secuencia en PostgreSQL suele ser 'nombretabla_nombrecolumna_seq'
                sequence_name = f"{table_name}_id_seq"
                # Esta sentencia ajusta el próximo valor de la secuencia al valor máximo + 1
                connection.execute(text(f"SELECT setval('{sequence_name}', (SELECT COALESCE(MAX(id), 1) FROM {table_name}), true);"))

        print(f"   ✅ {len(df)} filas insertadas en '{table_name}'.")

    except Exception as e:
        print(f"   ❌ Error al insertar en '{table_name}': {e}")
        print(f"   Revisa que el esquema de la tabla '{table_name}' coincida y que las claves foráneas existan.")


# ==============================================================================
# --- Bloque de Ejecución Principal ---
# ==============================================================================

if __name__ == '__main__':
    # 🚨 Importante: Definir los headers para el Web Scraping
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 1. Generar todos los datos
    try:
        datos_generados = scrapear_y_simular(estado="baja-california-ensenada", tipo="renta", num_arrendatarios=85)
    except Exception as e:
        print(f"\n❌ Hubo un error al generar los datos (posiblemente en el web scraping). Deteniendo la ejecución. Error: {e}")
        exit()

    # 2. Conectar a la base de datos
    print("\n🔗 Conectando a la base de datos...")
    try:
        # Crea el motor de conexión
        engine = create_engine(DATABASE_URL)
        # Prueba la conexión
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("   Conexión exitosa a PostgreSQL.")
    except Exception as e:
        print(f"   ❌ Fallo la conexión a PostgreSQL. Revisa tus credenciales, host, puerto y que la base de datos exista. Error: {e}")
        exit()

    # 3. Insertar datos en ORDEN para respetar las claves foráneas (FK)

    print("\n📦 Comenzando la inserción en la base de datos...")

    # A. Catálogos (Sin FK)
    insertar_a_postgres(datos_generados['catalogo_muebles'], 'catalogo_muebles', engine)
    insertar_a_postgres(datos_generados['catalogo_servicios'], 'catalogo_servicios', engine)

    # B. Maestras (Sin FK o con FK a una tabla ya insertada)
    insertar_a_postgres(datos_generados['arrendatarios'], 'arrendatarios', engine)

    # C. Rentas (FK a arrendatarios)
    insertar_a_postgres(datos_generados['rentas'], 'rentas', engine)

    # D. Tablas de Relación (FK a rentas, catálogos)
    insertar_a_postgres(datos_generados['renta_muebles'], 'renta_muebles', engine)
    insertar_a_postgres(datos_generados['renta_servicios'], 'renta_servicios', engine)

    # E. Historial (FK a rentas)
    insertar_a_postgres(datos_generados['historial_renta'], 'historial_renta', engine)
    
    print("\n🎉 Proceso de inserción de datos completado exitosamente.")