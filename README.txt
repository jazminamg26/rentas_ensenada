# Resumen Esencial – API “Rentas Ensenada”

API REST para gestionar **inmuebles en renta**, **arrendatarios**, **muebles** y **servicios**, construida con **FastAPI**, **SQLModel** y **JWT** para autenticación por roles (*super_user* y *arrendatario*).

## ⚙️ Instalación rápida
```bash
python -m venv venv
source venv/bin/activate
pip install fastapi[standard] uvicorn sqlmodel bcrypt python-jose psycopg2-binary


## 🗄️ Base de datos

Configura DATABASE_URL en database.py (PostgreSQL o SQLite).


## ▶️ Ejecutar la API
uvicorn main:app --reload

Disponible en: http://127.0.0.1:8000

## 🔑 Autenticación

Login en POST /token

Usa el token en Swagger: http://127.0.0.1:8000/docs

##  🏠 Endpoints clave

Públicos
- GET /rentas_inmuebles
- GET /rentas_inmuebles/{id}
- GET /catalogo/muebles

Protegidos (requieren token)
- Crear/editar rentas
- Asignar/eliminar muebles
- Crear catálogo
- Registrar arrendatarios

## 📁 Estructura del proyecto

main.py – Rutas y autenticación
models.py – Modelos SQLModel
schemas.py – Validaciones Pydantic
database.py – Conexión a la base de datos

database.py – Conexión a la base de datos
