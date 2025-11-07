# -*- coding: utf-8 -*-
"""
Created on Mon Nov  3 09:20:46 2025

@author: Jazmin
"""

import pandas as pd
import time
import random
import requests
from bs4 import BeautifulSoup
import re
import json
from tqdm import tqdm
from unidecode import unidecode

pd.set_option('display.float_format', '{:.10f}'.format)

def limpia_texto(text):
    if text is None:
        return ""
    # Elimina caracteres no alfanuméricos, caracteres, puntuación, espacios extras y signos de pesos
    cleaned_text = re.sub(r'[^\w\s.]', '', text).strip()
    # Minúsculas
    cleaned_text = cleaned_text.lower()
    #Eliminar acentos
    cleaned_text = unidecode(cleaned_text)
    return cleaned_text

def limpia_moneda(text):
    if text is None:
        return ""
    #Eliminar "\n"
    cleaned_coin = re.sub(r'\n', '', text).strip()
    #Elimina comas
    cleaned_coin = re.sub(r',', '', text).strip()
    #Eliminar signo de pesos
    cleaned_coin = re.sub(r'$', '', cleaned_coin)

    return cleaned_coin


def limpia_datos(df):
    df = df.reset_index(drop=True)
   
    #Eliminar registros con precio 0 o nan
    df=df[df['precio']>0]
    df=df[df['precio'].notna()]
    #Eliminar registros que en oferta contengan "terreno"
    df=df[~df['oferta'].str.contains('terreno')]
    df=df[~df['oferta'].str.contains('remodelar')]
    df=df[~df['oferta'].str.contains('hectareas')]
    #Si la fuente es goodlers, sacar el promedio de precio_min y precio_max y ponerlo en precio
    #Eliminar registros con misma oferta y mismo precio
    df=df.drop_duplicates(subset=['oferta','precio','recamaras','bathrooms'],keep='first')
    #Calcular precio por metro cuadrado
    df['precio_m2'] = df['precio'] / df['mts']

    return df



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}



def icasas(estado, tipo="renta"):
    if tipo== "venta":
        base_url = "https://www.icasas.mx/venta/habitacionales-casas-{}-2_5_3_0_11_0/t_departamentos/p_{}"
    elif tipo== "renta":
        base_url = "https://www.icasas.mx/renta/habitacionales-casas-{}-2_5_3_0_11_0/t_departamentos/p_{}"
    else:
        raise ValueError("Tipo de propiedad no válido. Usa 'venta' o 'renta'.")
    all_data=pd.DataFrame()
    for paginas in tqdm(range(1, 101), desc=f"Scrapeando icasas en {estado}"):
        url= base_url.format(estado, paginas)
        r=requests.get(url, headers=headers)
        soup=BeautifulSoup(r.text, 'html.parser')
        resultados=soup.find_all('li', class_='serp-snippet ad featured')
        oferta, precio, superficie, recamaras, bathrooms, lat, lon = [], [], [], [], [], [], []
        for i in resultados:
            a_tag = i.find('a', class_='detail-redirection')
            oferta.append(a_tag.get_text(strip=True) if a_tag else None)
            superficie.append(i.find('span', class_='areaBuilt').get_text(strip=True) if i.find('span', class_='areaBuilt') else None)
            recamaras.append(i.find('span', class_='rooms').get_text(strip=True) if i.find('span', class_='rooms') else None)
            bathrooms.append(i.find('span', class_='bathrooms').get_text(strip=True) if i.find('span', class_='bathrooms') else None)
            lat_tag = i.find('meta', itemprop='latitude')
            lon_tag = i.find('meta', itemprop='longitude')
            lat.append(lat_tag['content'] if lat_tag else None)
            lon.append(lon_tag['content'] if lon_tag else None)
            precio.append(i.find('div', class_='price').get_text(strip=True) if i.find('div', class_='price') else None)


        #Imprimir lens de cada lista
        temp = pd.DataFrame({'oferta': oferta, 'precio':precio, 'mts': superficie, 'recamaras': recamaras, 'bathrooms': bathrooms, 'lat': lat, 'lon': lon})
        all_data = pd.concat([all_data, temp], ignore_index=True)
    all_data["fecha_consulta"] = pd.to_datetime("today")
    all_data["fuente"] = "icasas"
    all_data["oferta"] = all_data["oferta"].apply(limpia_texto)
    #Limpiar precio
    all_data["precio"] = all_data["precio"].apply(limpia_moneda)
#Eliminar todo lo que viene después de "MX"
    #all_data["precio"] = all_data["precio"].apply(lambda x: re.sub(r'MX.*', '', x))
    # Elimina texto como "(Precio a consultar)" o "destacado"
    all_data["precio"] = all_data["precio"].astype(str)
    all_data["precio"] = all_data["precio"].str.extract(r'(\d+(?:\.\d+)?)')  # Extrae solo el número# Convierte a numérico de forma segura
    all_data["precio"] = pd.to_numeric(all_data["precio"], errors="coerce")
    all_data["mts"]= all_data["mts"].astype(str)
    all_data["mts"] = all_data["mts"].str.extract(r'(\d+)')
    all_data["mts"] = pd.to_numeric(all_data["mts"], errors="coerce")
    all_data["mts"] = all_data["mts"].astype(float)
    all_data["precio"] = all_data["precio"].astype(float)

    return all_data


#renta
vivi_renta=icasas("baja-california-ensenada","renta")
vivi_renta

vivi_limpia_renta=vivi_renta.copy()
#Eliminar si oferta dice "lote" o "terreno"
vivi_limpia_renta=vivi_limpia_renta[~vivi_limpia_renta["oferta"].str.contains("lote|terreno|renta")]
#Eliminar si lat es nulo
vivi_limpia_renta=vivi_limpia_renta[vivi_limpia_renta['lat'].notna()]
#Aplicar función de limpieza
vivi_limpia_renta=limpia_datos(vivi_limpia_renta)
vivi_limpia_renta


vivi_limpia_renta['precio'] = vivi_limpia_renta['precio'].apply(lambda x: f"{x:.10f}")
vivi_limpia_renta['precio'] = vivi_limpia_renta['precio'].astype(float).round(0).astype(int)


vivi_limpia_renta.to_csv("archivos/viviendas_icasas_renta.csv",index=False)
