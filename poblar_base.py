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
from sqlalchemy import text

# Configuración de Pandas
pd.set_option('display.float_format', '{:.10f}'.format)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

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

# --- 4. Función de Simulación de Arrendatarios ---

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


# --- 5. Función Principal de Generación (Reemplaza todos los pasos con CSV) ---

def scrapear_y_simular(estado="baja-california-ensenada", tipo="renta", num_arrendatarios=85):
    
    print("🚀 Iniciando Web Scraping y Simulación...")

    # A. Scrapeo y Limpieza Inicial de Viviendas (Renta)
    vivi_renta = icasas(estado, tipo)
    
    # --- Limpieza de recamaras antes de la limpieza general ---
    # 1. Extraer solo el número de la columna recamaras (si el scraper no lo hizo completamente)
    vivi_renta["recamaras"] = vivi_renta["recamaras"].astype(str).str.extract(r'(\d+)')
    # 2. Convertir a numérico (entero, forzando NaN si falla)
    vivi_renta["recamaras"] = pd.to_numeric(vivi_renta["recamaras"], errors="coerce").astype('Int64') # Int64 soporta NaN
    # ---------------------------------------------------------
    
    vivi_limpia_renta = vivi_renta.copy()
    vivi_limpia_renta = vivi_limpia_renta[~vivi_limpia_renta["oferta"].str.contains("lote|terreno|renta")]
    vivi_limpia_renta = vivi_limpia_renta[vivi_limpia_renta['lat'].notna()]
    vivi_limpia_renta = limpia_datos(vivi_limpia_renta) # Esta función también podría necesitar 'recamaras' como numérico
    vivi_limpia_renta['precio'] = vivi_limpia_renta['precio'].round(0).astype(int)





    # B. Generar Arrendatarios
    arrendatarios_df = generar_arrendatarios(n=num_arrendatarios)
    print(f"✅ Generados {len(arrendatarios_df)} arrendatarios.")
    
    # C. Simulación de Renta Inmuebles
    renta = vivi_limpia_renta.copy()
    renta['Edificio'] = np.random.choice(['Casa', 'Departamento'], size=len(renta))
    
    # ESTA LÍNEA AHORA FUNCIONARÁ CORRECTAMENTE porque 'recamaras' es Int64
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
        "historialrenta": historial_renta,
        "renta_muebles": renta_muebles,
        "renta_servicios": renta_servicios,
        "catalogo_muebles": CATALOGOS['muebles'],
        "catalogo_servicios": CATALOGOS['servicios'],
    }

# --- 6. Función de Llenado de Base de Datos sin Archivos CSV ---

# NOTA: Las funciones 'truncate_tables' y 'create_users_from_arrendatarios' 
# y los modelos/engine se asumen definidos y accesibles desde los archivos 'database.py', 'models.py', etc.

def fill_database_no_csv(data_dfs):
    """Función principal para llenar todas las tablas sin usar CSVs."""
    
    print("--- 🛠️ Iniciando carga masiva de datos a la BDD (sin CSV) ---")

    # Mapeo de modelos a DataFrames generados
    MODEL_MAP = {
        Arrendatario: "arrendatarios",
        Renta: "rentas",
        HistorialRenta: "historialrenta",
        RentaMuebles: "renta_muebles",
        RentaServicios: "renta_servicios",
        CatalogoMuebles: "catalogo_muebles",
        CatalogoServicios: "catalogo_servicios",
    }
    
    # Simulación de mapeo (necesitas implementar la conexión real)
    engine = None # Reemplazar con tu motor de SQLModel/SQLAlchemy
    if engine is None:
        print("❌ Error: El motor de la base de datos (engine) no está definido. Deteniendo la carga a la BDD.")
        return

    try:
        with Session(engine) as session:
            
            # --- LLAMADA A LA FUNCIÓN DE VACIADO (Asume que está definida) ---
            # truncate_tables(session)
            print("Función truncate_tables() omitida por falta de 'engine'.")
            # ----------------------------------------------------------------

            # 1. Cargar Catálogos
            print("Cargando Catálogos...")
            for model, key in [(CatalogoMuebles, "catalogo_muebles"), (CatalogoServicios, "catalogo_servicios")]:
                df = data_dfs[key].copy().drop(columns=['id'], errors='ignore')
                data = df.to_dict('records')
                session.add_all([model(**item) for item in data])
                print(f"✅ Catálogo '{model.__name__}' cargado.")

            # 2. Crear Users y Arrendatarios (Dependencia de User)
            print("Creando usuarios y preparando arrendatarios...")
            df_arrendatarios = data_dfs["arrendatarios"].copy()
            # Esta función DEBE crear los Users y modificar el DF con el 'user_id' de la BDD.
            # df_arrendatarios_for_db = create_users_from_arrendatarios(df_arrendatarios, session)
            print("Función create_users_from_arrendatarios() omitida por falta de 'get_password_hash'.")
            
            # **NOTA**: Por la omisión de la función, se salta la carga de Arrendatarios y Users 
            # para evitar errores, pero en tu código real DEBERÍAS insertarlos aquí.

            # Asumiremos que los IDs de arrendatario siguen siendo correctos para la siguiente tabla.
            df_rentas_original = data_dfs["rentas"].copy()
            renta_ids_csv = df_rentas_original['id'].tolist()
            
            # 3. Cargar Rentas
            print("Cargando Rentas...")
            df_rentas = df_rentas_original.copy().drop(columns=['id'], errors='ignore')
            data_rentas = df_rentas.to_dict('records')
            session.add_all([Renta(**item) for item in data_rentas])
            session.commit()
            print("✅ Rentas cargadas correctamente.")
            
            # Obtener el mapeo de IDs de Renta reales (CSV_ID -> DB_ID)
            # Esto asume que no hubo omisiones o reordenamientos en la BDD.
            renta_ids_db = session.exec(select(Renta.id)).all()
            id_map = {csv_id: db_id for csv_id, db_id in zip(renta_ids_csv, renta_ids_db)}
            
            # 4. Cargar Historial de Rentas
            print("Cargando Historial de Rentas...")
            df_historial = data_dfs["historialrenta"].copy().drop(columns=['id'], errors='ignore')
            df_historial['renta_id'] = df_historial['renta_id'].map(id_map)
            df_historial['fecha_inicio'] = pd.to_datetime(df_historial['fecha_inicio']).dt.date
            df_historial['fecha_fin'] = pd.to_datetime(df_historial['fecha_fin']).dt.date
            data_historial = df_historial.to_dict('records')
            session.add_all([HistorialRenta(**item) for item in data_historial])
            print("✅ Historial de Rentas cargado.")

            # 5. Cargar Renta Muebles y Renta Servicios
            print("Cargando tablas de enlace...")
            for model, key in [(RentaMuebles, "renta_muebles"), (RentaServicios, "renta_servicios")]:
                df = data_dfs[key].copy().drop(columns=['id'], errors='ignore')
                df['renta_id'] = df['renta_id'].map(id_map)
                data = df.to_dict('records')
                session.add_all([model(**item) for item in data])
                print(f"✅ Tabla de enlace '{model.__name__}' cargada.")

            session.commit()
            print("\n🎉 Todos los datos han sido cargados exitosamente sin usar CSVs.")

    except Exception as e:
        print(f"\nFATAL ERROR durante la carga de datos a la BDD: {e}")

# --- Ejecución Principal (Demostración) ---
if __name__ == "__main__":
    
    # 1. Generar todos los datos en DataFrames en memoria
    datos_generados = scrapear_y_simular()
    
    # 2. Opcional: Imprimir un ejemplo
    # print("\nEjemplo de Renta generada:")
    # print(datos_generados['rentas'].head())
    
    # 3. Cargar los datos a la Base de Datos (requiere que 'engine' esté configurado)
    # fill_database_no_csv(datos_generados) # Descomenta para ejecutar la carga real a la BDD
    print("\nLa función fill_database_no_csv ha sido omitida en la ejecución final por las dependencias de BDD.")