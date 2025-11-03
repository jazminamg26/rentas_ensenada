# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 09:59:21 2025

@author: Jazmin
"""

import pandas as pd
import numpy as np
import random
import unicodedata

num_arrendatarios = 85

# Simulación de los arrendatarios ----------------------------------------

nombres = [
    "Carlos", "María", "José", "Ana", "Luis", "Laura", "Miguel", "Sofía", "Jorge", "Fernanda",
    "Andrés", "Patricia", "Ricardo", "Lucía", "Héctor", "Diana", "Sergio", "Camila", "Raúl", "Valeria"
]

apellidos = [
    "Hernández", "García", "Martínez", "López", "González", "Rodríguez", "Pérez", "Sánchez", "Ramírez", "Flores",
    "Torres", "Díaz", "Vargas", "Cruz", "Morales", "Gómez", "Castro", "Rojas", "Ruiz", "Jiménez"
]

def quitar_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def generar_arrendatario():
    nombre = random.choice(nombres)
    apellido = random.choice(apellidos)
    nombre_completo = f"{nombre} {apellido}"

    # Teléfono con prefijo 646 y 7 dígitos aleatorios
    telefono = "646" + "".join(str(random.randint(0, 9)) for _ in range(7))

    # 70% de probabilidad de tener correo
    if random.random() < 0.7:
        nombre_sin_acentos = quitar_acentos(nombre.lower())
        apellido_sin_acentos = quitar_acentos(apellido.lower())
        numero_extra = random.randint(1, 9999)
        correo = f"{nombre_sin_acentos}.{apellido_sin_acentos}{numero_extra}@gmail.com"
    else:
        correo = None

    return {
        "nombre": nombre_completo,
        "telefono": telefono,
        "correo": correo
    }

def generar_arrendatarios(n=10):
    arrendatarios = [generar_arrendatario() for _ in range(n)]
    df = pd.DataFrame(arrendatarios)
    df.insert(0, "id", range(1, n + 1))  # columna id autoincremental
    return df

arrendatarios_df = generar_arrendatarios(n=num_arrendatarios)
print(arrendatarios_df)

# Simulación de las rentas inmuebles -------------------------------------
# Cargar el CSV original
vivi_limpia_renta = pd.read_csv("viviendas_icasas_renta.csv")

# Simular columna "Edificio"
vivi_limpia_renta['Edificio'] = np.random.choice(['Casa', 'Departamento'], size=len(vivi_limpia_renta))

# Simular columna "Banos"
vivi_limpia_renta['Banos'] = vivi_limpia_renta['recamaras'].apply(
    lambda x: 1 if x <= 2 else np.random.choice([1, 2])
)

# Simular columna "Mascotas"
vivi_limpia_renta['Mascotas'] = np.random.choice([True, False], size=len(vivi_limpia_renta))

# Simular columna "Tinaco"
vivi_limpia_renta['Tinaco'] = np.random.choice([True, False], size=len(vivi_limpia_renta))

# Simular columna "Estacionamiento"
vivi_limpia_renta['Estacionamiento'] = np.random.choice([0, 1], size=len(vivi_limpia_renta))

# Simular columna "Activo" (90% True)
vivi_limpia_renta['Activo'] = np.random.choice([True, False], size=len(vivi_limpia_renta), p=[0.9, 0.1])

# Simular columna "Disponible" (80% True)
vivi_limpia_renta['Disponible'] = np.random.choice([True, False], size=len(vivi_limpia_renta), p=[0.8, 0.2])

# Eliminar columnas innecesarias
vivi_limpia_renta = vivi_limpia_renta.drop(columns=['mts', 'bathrooms', 'fecha_consulta', 'precio_m2'])

# Asignar arrendatarios
n_filas = len(vivi_limpia_renta)
numeros = np.arange(1, num_arrendatarios + 1)

# Repetir números si hay más filas que arrendatarios
if n_filas > num_arrendatarios:
    numeros = np.concatenate([numeros, np.random.choice(numeros, size=n_filas - num_arrendatarios, replace=True)])

# Mezclar los números
np.random.shuffle(numeros)

# Asignar al DataFrame
vivi_limpia_renta['arrendatario_id'] = numeros

# Renombrar columna recamaras a habitaciones
vivi_limpia_renta = vivi_limpia_renta.rename(columns={"recamaras": "habitaciones"}, errors="raise")

# Crear columna 'id' con el índice de cada fila comenzando en 1
vivi_limpia_renta['id'] = vivi_limpia_renta.index + 1

# Reordenar columnas
columnas_ordenadas = [
    'id',
    'Edificio',
    'habitaciones',
    'Banos',
    'lat',
    'lon',
    'Mascotas',
    'Tinaco',
    'Estacionamiento',
    'Activo',
    'Disponible',
    'precio',
    'arrendatario_id'
]

vivi_limpia_renta = vivi_limpia_renta[columnas_ordenadas]

# Verificar resultado
print(vivi_limpia_renta.head())

# Convertir todas las columnas a minúsculas
vivi_limpia_renta.columns = [col.lower() for col in vivi_limpia_renta.columns]

# Verificar
renta = vivi_limpia_renta.copy()





import pandas as pd
import numpy as np
import random

# Cargar catálogo de muebles
catalogo_muebles = pd.read_csv("catalogo_muebles.csv")

# Supongamos que ya tienes tu DataFrame 'renta' con columna 'id'
# Por ejemplo: renta = pd.read_csv("renta.csv")

# Lista para guardar filas de renta_muebles
filas = []

# Para cada renta_id en renta
for renta_id in renta['id']:
    # Elegir aleatoriamente cuántos muebles tendrá esta renta (0 a número total de muebles)
    num_muebles = random.randint(0, len(catalogo_muebles))
    
    # Si tiene muebles
    if num_muebles > 0:
        # Elegir muebles aleatoriamente sin repetición
        muebles_seleccionados = random.sample(list(catalogo_muebles['id']), k=num_muebles)
        
        # Agregar filas
        for mueble_id in muebles_seleccionados:
            filas.append({
                'renta_id': renta_id,
                'renta_mueble': mueble_id
            })

# Crear DataFrame
renta_muebles = pd.DataFrame(filas)

# Crear columna 'id' como índice
renta_muebles.insert(0, 'id', range(1, len(renta_muebles) + 1))

# Ver ejemplo
print(renta_muebles.head())
