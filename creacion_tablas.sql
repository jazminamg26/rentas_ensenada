/* CREATE DATABASE rentasInmuebles_ensenada; */

CREATE TABLE catalogo_muebles (
	id SERIAL PRIMARY KEY,
	mueble VARCHAR(20)
);

CREATE TABLE catalogo_servicios (
	id SERIAL PRIMARY KEY,
	servicio VARCHAR(20)
);

CREATE TABLE arrendatarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(150),
    activo BOOLEAN
);


CREATE TABLE rentas (
    id SERIAL PRIMARY KEY,
    edificio VARCHAR(20),
    habitaciones INTEGER,
    banos FLOAT,
    lat FLOAT,
    lon FLOAT,
    mascotas BOOLEAN,
    tinaco BOOLEAN,
    estacionamiento INTEGER,
    activo BOOLEAN,
    disponible BOOLEAN,
    precio INTEGER,
    arrendatario_id INTEGER REFERENCES arrendatarios(id)
);


CREATE TABLE renta_muebles (
    id SERIAL PRIMARY KEY,
    renta_id INTEGER REFERENCES rentas(id),
    mueble_id INTEGER REFERENCES catalogo_muebles(id)
);


CREATE TABLE renta_servicios (
    id SERIAL PRIMARY KEY,
    renta_id INTEGER REFERENCES rentas(id),
    servicio_id INTEGER REFERENCES catalogo_servicios(id)
);


CREATE TABLE historial_renta (
    id SERIAL PRIMARY KEY,
    renta_id INTEGER REFERENCES rentas(id),
    fecha_inicio DATE,
    fecha_fin DATE,
    precio INTEGER
);


