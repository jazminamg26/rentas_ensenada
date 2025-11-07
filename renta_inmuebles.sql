--
-- PostgreSQL database dump
--

\restrict PReAY8Sh5alAYeBV4W8JARQWrC9vpVQdD3zpRLnfGgHwJgmzgIQEdG5GzoHd0L9

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

-- Started on 2025-11-07 17:09:44

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5076 (class 1262 OID 16578)
-- Name: rentasInmuebles_ensenada; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE "rentasInmuebles_ensenada" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.1252';


ALTER DATABASE "rentasInmuebles_ensenada" OWNER TO postgres;

\unrestrict PReAY8Sh5alAYeBV4W8JARQWrC9vpVQdD3zpRLnfGgHwJgmzgIQEdG5GzoHd0L9
\connect "rentasInmuebles_ensenada"
\restrict PReAY8Sh5alAYeBV4W8JARQWrC9vpVQdD3zpRLnfGgHwJgmzgIQEdG5GzoHd0L9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 226 (class 1259 OID 16617)
-- Name: arrendatario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.arrendatario (
    id integer NOT NULL,
    nombre character varying NOT NULL,
    telefono character varying NOT NULL,
    correo character varying,
    activo boolean NOT NULL,
    user_id integer
);


ALTER TABLE public.arrendatario OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16616)
-- Name: arrendatario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.arrendatario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.arrendatario_id_seq OWNER TO postgres;

--
-- TOC entry 5077 (class 0 OID 0)
-- Dependencies: 225
-- Name: arrendatario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.arrendatario_id_seq OWNED BY public.arrendatario.id;


--
-- TOC entry 222 (class 1259 OID 16595)
-- Name: catalogo_muebles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.catalogo_muebles (
    id integer NOT NULL,
    mueble character varying NOT NULL
);


ALTER TABLE public.catalogo_muebles OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16594)
-- Name: catalogo_muebles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.catalogo_muebles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.catalogo_muebles_id_seq OWNER TO postgres;

--
-- TOC entry 5078 (class 0 OID 0)
-- Dependencies: 221
-- Name: catalogo_muebles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.catalogo_muebles_id_seq OWNED BY public.catalogo_muebles.id;


--
-- TOC entry 224 (class 1259 OID 16606)
-- Name: catalogo_servicios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.catalogo_servicios (
    id integer NOT NULL,
    servicio character varying NOT NULL
);


ALTER TABLE public.catalogo_servicios OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16605)
-- Name: catalogo_servicios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.catalogo_servicios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.catalogo_servicios_id_seq OWNER TO postgres;

--
-- TOC entry 5079 (class 0 OID 0)
-- Dependencies: 223
-- Name: catalogo_servicios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.catalogo_servicios_id_seq OWNED BY public.catalogo_servicios.id;


--
-- TOC entry 230 (class 1259 OID 16663)
-- Name: historialrenta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.historialrenta (
    id integer NOT NULL,
    renta_id integer NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    precio integer NOT NULL
);


ALTER TABLE public.historialrenta OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16662)
-- Name: historialrenta_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.historialrenta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historialrenta_id_seq OWNER TO postgres;

--
-- TOC entry 5080 (class 0 OID 0)
-- Dependencies: 229
-- Name: historialrenta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.historialrenta_id_seq OWNED BY public.historialrenta.id;


--
-- TOC entry 228 (class 1259 OID 16636)
-- Name: renta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.renta (
    id integer NOT NULL,
    edificio character varying NOT NULL,
    habitaciones integer NOT NULL,
    banos double precision NOT NULL,
    lat double precision NOT NULL,
    lon double precision NOT NULL,
    mascotas boolean NOT NULL,
    tinaco boolean NOT NULL,
    estacionamiento integer NOT NULL,
    activo boolean NOT NULL,
    disponible boolean NOT NULL,
    precio integer NOT NULL,
    arrendatario_id integer NOT NULL
);


ALTER TABLE public.renta OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16635)
-- Name: renta_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.renta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.renta_id_seq OWNER TO postgres;

--
-- TOC entry 5081 (class 0 OID 0)
-- Dependencies: 227
-- Name: renta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.renta_id_seq OWNED BY public.renta.id;


--
-- TOC entry 232 (class 1259 OID 16680)
-- Name: renta_muebles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.renta_muebles (
    id integer NOT NULL,
    renta_id integer NOT NULL,
    mueble_id integer NOT NULL
);


ALTER TABLE public.renta_muebles OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16679)
-- Name: renta_muebles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.renta_muebles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.renta_muebles_id_seq OWNER TO postgres;

--
-- TOC entry 5082 (class 0 OID 0)
-- Dependencies: 231
-- Name: renta_muebles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.renta_muebles_id_seq OWNED BY public.renta_muebles.id;


--
-- TOC entry 234 (class 1259 OID 16700)
-- Name: renta_servicios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.renta_servicios (
    id integer NOT NULL,
    renta_id integer NOT NULL,
    servicio_id integer NOT NULL
);


ALTER TABLE public.renta_servicios OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16699)
-- Name: renta_servicios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.renta_servicios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.renta_servicios_id_seq OWNER TO postgres;

--
-- TOC entry 5083 (class 0 OID 0)
-- Dependencies: 233
-- Name: renta_servicios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.renta_servicios_id_seq OWNED BY public.renta_servicios.id;


--
-- TOC entry 220 (class 1259 OID 16580)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying NOT NULL,
    role character varying(20) NOT NULL,
    active boolean NOT NULL
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16579)
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO postgres;

--
-- TOC entry 5084 (class 0 OID 0)
-- Dependencies: 219
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- TOC entry 4894 (class 2604 OID 16620)
-- Name: arrendatario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.arrendatario ALTER COLUMN id SET DEFAULT nextval('public.arrendatario_id_seq'::regclass);


--
-- TOC entry 4892 (class 2604 OID 16598)
-- Name: catalogo_muebles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.catalogo_muebles ALTER COLUMN id SET DEFAULT nextval('public.catalogo_muebles_id_seq'::regclass);


--
-- TOC entry 4893 (class 2604 OID 16609)
-- Name: catalogo_servicios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.catalogo_servicios ALTER COLUMN id SET DEFAULT nextval('public.catalogo_servicios_id_seq'::regclass);


--
-- TOC entry 4896 (class 2604 OID 16666)
-- Name: historialrenta id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historialrenta ALTER COLUMN id SET DEFAULT nextval('public.historialrenta_id_seq'::regclass);


--
-- TOC entry 4895 (class 2604 OID 16639)
-- Name: renta id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta ALTER COLUMN id SET DEFAULT nextval('public.renta_id_seq'::regclass);


--
-- TOC entry 4897 (class 2604 OID 16683)
-- Name: renta_muebles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta_muebles ALTER COLUMN id SET DEFAULT nextval('public.renta_muebles_id_seq'::regclass);


--
-- TOC entry 4898 (class 2604 OID 16703)
-- Name: renta_servicios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta_servicios ALTER COLUMN id SET DEFAULT nextval('public.renta_servicios_id_seq'::regclass);


--
-- TOC entry 4891 (class 2604 OID 16583)
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- TOC entry 4907 (class 2606 OID 16628)
-- Name: arrendatario arrendatario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.arrendatario
    ADD CONSTRAINT arrendatario_pkey PRIMARY KEY (id);


--
-- TOC entry 4903 (class 2606 OID 16604)
-- Name: catalogo_muebles catalogo_muebles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.catalogo_muebles
    ADD CONSTRAINT catalogo_muebles_pkey PRIMARY KEY (id);


--
-- TOC entry 4905 (class 2606 OID 16615)
-- Name: catalogo_servicios catalogo_servicios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.catalogo_servicios
    ADD CONSTRAINT catalogo_servicios_pkey PRIMARY KEY (id);


--
-- TOC entry 4912 (class 2606 OID 16673)
-- Name: historialrenta historialrenta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historialrenta
    ADD CONSTRAINT historialrenta_pkey PRIMARY KEY (id);


--
-- TOC entry 4914 (class 2606 OID 16688)
-- Name: renta_muebles renta_muebles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta_muebles
    ADD CONSTRAINT renta_muebles_pkey PRIMARY KEY (id);


--
-- TOC entry 4910 (class 2606 OID 16656)
-- Name: renta renta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta
    ADD CONSTRAINT renta_pkey PRIMARY KEY (id);


--
-- TOC entry 4916 (class 2606 OID 16708)
-- Name: renta_servicios renta_servicios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta_servicios
    ADD CONSTRAINT renta_servicios_pkey PRIMARY KEY (id);


--
-- TOC entry 4901 (class 2606 OID 16592)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 4908 (class 1259 OID 16634)
-- Name: ix_arrendatario_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_arrendatario_user_id ON public.arrendatario USING btree (user_id);


--
-- TOC entry 4899 (class 1259 OID 16593)
-- Name: ix_user_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_user_username ON public."user" USING btree (username);


--
-- TOC entry 4917 (class 2606 OID 16629)
-- Name: arrendatario arrendatario_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.arrendatario
    ADD CONSTRAINT arrendatario_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- TOC entry 4919 (class 2606 OID 16674)
-- Name: historialrenta historialrenta_renta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historialrenta
    ADD CONSTRAINT historialrenta_renta_id_fkey FOREIGN KEY (renta_id) REFERENCES public.renta(id);


--
-- TOC entry 4918 (class 2606 OID 16657)
-- Name: renta renta_arrendatario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta
    ADD CONSTRAINT renta_arrendatario_id_fkey FOREIGN KEY (arrendatario_id) REFERENCES public.arrendatario(id);


--
-- TOC entry 4920 (class 2606 OID 16694)
-- Name: renta_muebles renta_muebles_mueble_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta_muebles
    ADD CONSTRAINT renta_muebles_mueble_id_fkey FOREIGN KEY (mueble_id) REFERENCES public.catalogo_muebles(id);


--
-- TOC entry 4921 (class 2606 OID 16689)
-- Name: renta_muebles renta_muebles_renta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta_muebles
    ADD CONSTRAINT renta_muebles_renta_id_fkey FOREIGN KEY (renta_id) REFERENCES public.renta(id);


--
-- TOC entry 4922 (class 2606 OID 16709)
-- Name: renta_servicios renta_servicios_renta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta_servicios
    ADD CONSTRAINT renta_servicios_renta_id_fkey FOREIGN KEY (renta_id) REFERENCES public.renta(id);


--
-- TOC entry 4923 (class 2606 OID 16714)
-- Name: renta_servicios renta_servicios_servicio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.renta_servicios
    ADD CONSTRAINT renta_servicios_servicio_id_fkey FOREIGN KEY (servicio_id) REFERENCES public.catalogo_servicios(id);


-- Completed on 2025-11-07 17:09:45

--
-- PostgreSQL database dump complete
--

\unrestrict PReAY8Sh5alAYeBV4W8JARQWrC9vpVQdD3zpRLnfGgHwJgmzgIQEdG5GzoHd0L9

