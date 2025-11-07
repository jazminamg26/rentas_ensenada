SELECT *
FROM renta_muebles;


SELECT *
FROM renta_servicios;


SELECT *
FROM catalogo_servicios;


SELECT *
FROM catalogo_muebles;


SELECT *
FROM arrendatario;


SELECT *
FROM renta;


SELECT *
FROM historial_renta



ALTER TABLE public.renta
ADD CONSTRAINT fk_renta_arrendatario
FOREIGN KEY (arrendatario_id)
REFERENCES public.arrendatario(id)
ON DELETE SET NULL;  -- o CASCADE, según tu lógica



ALTER TABLE public.historial_renta
ADD CONSTRAINT fk_historial_renta
FOREIGN KEY (renta_id)
REFERENCES public.renta(id)
ON DELETE CASCADE;


ALTER TABLE public.renta_muebles
ADD CONSTRAINT fk_renta_muebles_renta
FOREIGN KEY (renta_id)
REFERENCES public.renta(id)
ON DELETE CASCADE;

ALTER TABLE public.renta_muebles
ADD CONSTRAINT fk_renta_muebles_mueble
FOREIGN KEY (mueble_id)
REFERENCES public.catalogo_muebles(id)
ON DELETE CASCADE;


ALTER TABLE public.renta_servicios
ADD CONSTRAINT fk_renta_servicios_renta
FOREIGN KEY (renta_id)
REFERENCES public.renta(id)
ON DELETE CASCADE;

ALTER TABLE public.renta_servicios
ADD CONSTRAINT fk_renta_servicios_servicio
FOREIGN KEY (servicio_id)
REFERENCES public.catalogo_servicios(id)
ON DELETE CASCADE;


