--
-- PostgreSQL database dump
--

\restrict 6An17p1y3zFpabWAPg8qm7xshqRy8qkUTrWjl2yFyQgFKZTrBKXsWpL70pUGXRK

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-06-03 13:20:22

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
-- TOC entry 287 (class 1255 OID 24072)
-- Name: comprarentrada(integer, integer, integer); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.comprarentrada(IN p_idasistente integer, IN p_idproyeccion integer, IN p_idtarifa integer, OUT p_respuesta character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_Aforo     INT;
    v_Titulo    VARCHAR(150);
    v_FechaHora TIMESTAMP;
    v_YaCompro  INT;
BEGIN
    SELECT pr.AforoDisponible, pe.Titulo, pr.FechaHora
        INTO v_Aforo, v_Titulo, v_FechaHora
        FROM Proyecciones pr
        INNER JOIN Peliculas pe ON pe.IdPelicula = pr.IdPelicula
        WHERE pr.IdProyeccion = p_IdProyeccion;
    IF NOT FOUND THEN
        p_Respuesta := 'Error: La proyeccion indicada no existe.'; RETURN;
    END IF;
    SELECT COUNT(*) INTO v_YaCompro
        FROM Entradas
        WHERE IdAsistente = p_IdAsistente AND IdProyeccion = p_IdProyeccion;
    IF v_YaCompro > 0 THEN
        p_Respuesta := 'Error: El asistente ya tiene una entrada para esta proyeccion.'; RETURN;
    END IF;
    IF v_Aforo <= 0 THEN
        p_Respuesta := 'Lo sentimos, no hay aforo disponible para esta funcion.'; RETURN;
    END IF;
    INSERT INTO Entradas (IdAsistente, IdProyeccion, IdTarifa)
        VALUES (p_IdAsistente, p_IdProyeccion, p_IdTarifa);
    UPDATE Proyecciones
        SET AforoDisponible = AforoDisponible - 1
        WHERE IdProyeccion = p_IdProyeccion;
    p_Respuesta := 'Entrada registrada exitosamente para "' || v_Titulo ||
                   '" el ' || TO_CHAR(v_FechaHora, 'DD/MM/YYYY HH24:MI') || '.';
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error inesperado: ' || SQLERRM;
END; $$;


ALTER PROCEDURE public.comprarentrada(IN p_idasistente integer, IN p_idproyeccion integer, IN p_idtarifa integer, OUT p_respuesta character varying) OWNER TO postgres;

--
-- TOC entry 293 (class 1255 OID 24080)
-- Name: fn_call_comprarentrada(integer, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_call_comprarentrada(p_idasistente integer, p_idproyeccion integer, p_idtarifa integer) RETURNS TABLE(respuesta character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL ComprarEntrada(p_IdAsistente, p_IdProyeccion, p_IdTarifa, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;


ALTER FUNCTION public.fn_call_comprarentrada(p_idasistente integer, p_idproyeccion integer, p_idtarifa integer) OWNER TO postgres;

--
-- TOC entry 295 (class 1255 OID 24082)
-- Name: fn_call_programarproyeccion(integer, integer, integer, text, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_call_programarproyeccion(p_idpelicula integer, p_idsala integer, p_idedicion integer, p_fechahora text, p_tieneqa boolean) RETURNS TABLE(respuesta character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE v_id INT; v_resp VARCHAR(300);
BEGIN
    CALL ProgramarProyeccion(p_IdPelicula, p_IdSala, p_IdEdicion, p_FechaHora::TIMESTAMP, p_TieneQA, v_id, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;


ALTER FUNCTION public.fn_call_programarproyeccion(p_idpelicula integer, p_idsala integer, p_idedicion integer, p_fechahora text, p_tieneqa boolean) OWNER TO postgres;

--
-- TOC entry 294 (class 1255 OID 24081)
-- Name: fn_call_venderabono(integer, integer, integer, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_call_venderabono(p_idasistente integer, p_idtipoabono integer, p_idedicion integer, p_pagoexitoso boolean) RETURNS TABLE(respuesta character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL VenderAbono(p_IdAsistente, p_IdTipoAbono, p_IdEdicion, p_PagoExitoso, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;


ALTER FUNCTION public.fn_call_venderabono(p_idasistente integer, p_idtipoabono integer, p_idedicion integer, p_pagoexitoso boolean) OWNER TO postgres;

--
-- TOC entry 290 (class 1255 OID 24075)
-- Name: fn_controlagenda(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_controlagenda() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_Duracion    INT;
    v_FinNueva    TIMESTAMP;
    v_Conflicto   INT;
    v_TituloOcupa VARCHAR(150);
BEGIN
    SELECT Duracion INTO v_Duracion FROM Peliculas WHERE IdPelicula = NEW.IdPelicula;
    v_FinNueva := NEW.FechaHora + (v_Duracion + 30) * INTERVAL '1 minute';
    SELECT COUNT(*), MAX(pe.Titulo) INTO v_Conflicto, v_TituloOcupa
        FROM Proyecciones pr
        INNER JOIN Peliculas pe ON pe.IdPelicula = pr.IdPelicula
        WHERE pr.IdSala = NEW.IdSala
          AND pr.IdProyeccion <> COALESCE(NEW.IdProyeccion, -1)
          AND NEW.FechaHora < (pr.FechaHora + (pe.Duracion + 30) * INTERVAL '1 minute')
          AND v_FinNueva > pr.FechaHora;
    IF v_Conflicto > 0 THEN
        RAISE EXCEPTION
            'Control de Agenda: La sala ya esta ocupada por "%" en ese horario (incluidos 30 min de limpieza).',
            v_TituloOcupa;
    END IF;
    RETURN NEW;
END; $$;


ALTER FUNCTION public.fn_controlagenda() OWNER TO postgres;

--
-- TOC entry 289 (class 1255 OID 24074)
-- Name: programarproyeccion(integer, integer, integer, timestamp without time zone, boolean); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.programarproyeccion(IN p_idpelicula integer, IN p_idsala integer, IN p_idedicion integer, IN p_fechahora timestamp without time zone, IN p_tieneqa boolean, OUT p_idnuevo integer, OUT p_respuesta character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_Capacidad INT;
BEGIN
    SELECT Capacidad INTO v_Capacidad FROM Salas WHERE IdSala = p_IdSala;
    IF NOT FOUND THEN
        p_IdNuevo := NULL; p_Respuesta := 'Error: La sala indicada no existe.'; RETURN;
    END IF;
    INSERT INTO Proyecciones (IdPelicula, IdSala, IdEdicion, FechaHora, TieneQA, AforoDisponible)
        VALUES (p_IdPelicula, p_IdSala, p_IdEdicion, p_FechaHora, p_TieneQA, v_Capacidad)
        RETURNING IdProyeccion INTO p_IdNuevo;
    p_Respuesta := 'Proyeccion programada exitosamente. ID: ' || p_IdNuevo::TEXT;
EXCEPTION WHEN OTHERS THEN
    p_IdNuevo := NULL; p_Respuesta := 'Error: ' || SQLERRM;
END; $$;


ALTER PROCEDURE public.programarproyeccion(IN p_idpelicula integer, IN p_idsala integer, IN p_idedicion integer, IN p_fechahora timestamp without time zone, IN p_tieneqa boolean, OUT p_idnuevo integer, OUT p_respuesta character varying) OWNER TO postgres;

--
-- TOC entry 292 (class 1255 OID 24079)
-- Name: sp_reportefinanciero(); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.sp_reportefinanciero(OUT p_respuesta character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_TotalEntradas NUMERIC := 0;
    v_TotalAbonos NUMERIC := 0;
    r RECORD;
BEGIN
    RAISE NOTICE '=== INFORME FINANCIERO ===';
    FOR r IN (
        SELECT t.NombreTarifa, COUNT(e.IdEntrada) AS Cantidad, SUM(t.Precio) AS Subtotal
          FROM Entradas e INNER JOIN Tarifas t ON t.IdTarifa = e.IdTarifa
         GROUP BY t.NombreTarifa ORDER BY Subtotal DESC
    ) LOOP
        RAISE NOTICE 'Entrada - % | Cant: % | Subtotal: Bs. %', r.NombreTarifa, r.Cantidad, r.Subtotal;
        v_TotalEntradas := v_TotalEntradas + r.Subtotal;
    END LOOP;
    FOR r IN (
        SELECT ta.NombreAbono, COUNT(a.IdAbono) AS Cantidad, SUM(ta.Precio) AS Subtotal
          FROM Abonos a INNER JOIN TiposAbono ta ON ta.IdTipoAbono = a.IdTipoAbono
         WHERE a.Pagado = TRUE GROUP BY ta.NombreAbono ORDER BY Subtotal DESC
    ) LOOP
        RAISE NOTICE 'Abono - % | Cant: % | Subtotal: Bs. %', r.NombreAbono, r.Cantidad, r.Subtotal;
        v_TotalAbonos := v_TotalAbonos + r.Subtotal;
    END LOOP;
    RAISE NOTICE 'TOTAL GENERAL: Bs. %', v_TotalEntradas + v_TotalAbonos;
    p_Respuesta := 'Total general: Bs. ' || (v_TotalEntradas + v_TotalAbonos)::TEXT;
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error al generar informe: ' || SQLERRM;
END; $$;


ALTER PROCEDURE public.sp_reportefinanciero(OUT p_respuesta character varying) OWNER TO postgres;

--
-- TOC entry 291 (class 1255 OID 24078)
-- Name: sp_reportepremiacion(); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.sp_reportepremiacion(OUT p_respuesta character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE r RECORD;
BEGIN
    RAISE NOTICE '=== ACTA DE PREMIACION ===';
    FOR r IN (
        SELECT c.NombreCategoria, p.Titulo AS PeliculaGanadora,
               ROUND(AVG(ev.Puntuacion), 2) AS PromedioJurado, e.Anio
          FROM Premios pre
          INNER JOIN Categorias c ON c.IdCategoria = pre.IdCategoria
          INNER JOIN Peliculas p ON p.IdPelicula = pre.IdPelicula
          INNER JOIN Ediciones e ON e.IdEdicion = pre.IdEdicion
          INNER JOIN Evaluaciones ev ON ev.IdPelicula = pre.IdPelicula AND ev.IdCategoria = pre.IdCategoria
         GROUP BY c.NombreCategoria, p.Titulo, e.Anio
         ORDER BY c.NombreCategoria
    ) LOOP
        RAISE NOTICE 'Categoria: % | Ganadora: % | Promedio Jurado: %', r.NombreCategoria, r.PeliculaGanadora, r.PromedioJurado;
    END LOOP;
    p_Respuesta := 'Acta de premiacion generada exitosamente.';
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error al generar acta: ' || SQLERRM;
END; $$;


ALTER PROCEDURE public.sp_reportepremiacion(OUT p_respuesta character varying) OWNER TO postgres;

--
-- TOC entry 275 (class 1255 OID 24077)
-- Name: sp_reporteranking(); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.sp_reporteranking(OUT p_respuesta character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE r RECORD;
BEGIN
    RAISE NOTICE '=== RANKING DE PELICULAS ===';
    FOR r IN (
        SELECT p.Titulo,
               COUNT(e.IdEntrada) AS Asistentes,
               SUM(s.Capacidad) AS CapacidadTotal,
               ROUND(COUNT(e.IdEntrada) * 100.0 / NULLIF(SUM(s.Capacidad), 0), 2) AS PctOcupacion
          FROM Peliculas p
          INNER JOIN Proyecciones pr ON pr.IdPelicula = p.IdPelicula
          INNER JOIN Salas s ON s.IdSala = pr.IdSala
          LEFT JOIN Entradas e ON e.IdProyeccion = pr.IdProyeccion
         GROUP BY p.Titulo
         ORDER BY Asistentes DESC
    ) LOOP
        RAISE NOTICE 'Pelicula: % | Asistentes: % | Ocupacion: %', r.Titulo, r.Asistentes, r.PctOcupacion || '%';
    END LOOP;
    p_Respuesta := 'Ranking generado exitosamente.';
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error al generar ranking: ' || SQLERRM;
END; $$;


ALTER PROCEDURE public.sp_reporteranking(OUT p_respuesta character varying) OWNER TO postgres;

--
-- TOC entry 288 (class 1255 OID 24073)
-- Name: venderabono(integer, integer, integer, boolean); Type: PROCEDURE; Schema: public; Owner: postgres
--

CREATE PROCEDURE public.venderabono(IN p_idasistente integer, IN p_idtipoabono integer, IN p_idedicion integer, IN p_pagoexitoso boolean, OUT p_respuesta character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_CodigoAcceso VARCHAR(20);
    v_NombreAbono  VARCHAR(60);
    v_Precio       NUMERIC(10,2);
    v_NombreAsist  VARCHAR(100);
    v_NroAbono     INT;
BEGIN
    SELECT NombreAbono, Precio INTO v_NombreAbono, v_Precio
        FROM TiposAbono WHERE IdTipoAbono = p_IdTipoAbono;
    IF NOT FOUND THEN
        p_Respuesta := 'Error: El tipo de abono indicado no existe.'; RETURN;
    END IF;
    SELECT Nombre INTO v_NombreAsist
        FROM Asistentes WHERE IdAsistente = p_IdAsistente;
    IF NOT FOUND THEN
        p_Respuesta := 'Error: El asistente indicado no existe.'; RETURN;
    END IF;
    v_CodigoAcceso := 'AB-' || TO_CHAR(CURRENT_DATE, 'YYYY') || '-' ||
                      LPAD(CAST(FLOOR(RANDOM() * 90000 + 10000) AS TEXT), 5, '0');
    IF p_PagoExitoso = FALSE THEN
        RAISE EXCEPTION 'Pasarela de pago fallida. Operacion cancelada.';
    END IF;
    INSERT INTO Abonos (IdAsistente, IdTipoAbono, IdEdicion, CodigoAcceso, Pagado)
        VALUES (p_IdAsistente, p_IdTipoAbono, p_IdEdicion, v_CodigoAcceso, TRUE)
        RETURNING IdAbono INTO v_NroAbono;
    p_Respuesta := 'Abono registrado. Cod. acceso: ' || v_CodigoAcceso;
EXCEPTION WHEN OTHERS THEN
    p_Respuesta := 'Error: ' || SQLERRM;
END; $$;


ALTER PROCEDURE public.venderabono(IN p_idasistente integer, IN p_idtipoabono integer, IN p_idedicion integer, IN p_pagoexitoso boolean, OUT p_respuesta character varying) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 257 (class 1259 OID 23911)
-- Name: abonos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.abonos (
    idabono integer NOT NULL,
    idasistente integer NOT NULL,
    idtipoabono integer NOT NULL,
    idedicion integer NOT NULL,
    fechacompra timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    codigoacceso character varying(20) NOT NULL,
    pagado boolean DEFAULT false NOT NULL
);


ALTER TABLE public.abonos OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 23910)
-- Name: abonos_idabono_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.abonos_idabono_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.abonos_idabono_seq OWNER TO postgres;

--
-- TOC entry 5382 (class 0 OID 0)
-- Dependencies: 256
-- Name: abonos_idabono_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.abonos_idabono_seq OWNED BY public.abonos.idabono;


--
-- TOC entry 261 (class 1259 OID 23954)
-- Name: alojamientos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alojamientos (
    idalojamiento integer NOT NULL,
    idpersonal integer NOT NULL,
    idhotel integer NOT NULL,
    idedicion integer NOT NULL,
    nrohabitacion character varying(10) NOT NULL,
    checkin date NOT NULL,
    checkout date NOT NULL,
    CONSTRAINT ck_aloj_fechas CHECK ((checkout > checkin))
);


ALTER TABLE public.alojamientos OWNER TO postgres;

--
-- TOC entry 260 (class 1259 OID 23953)
-- Name: alojamientos_idalojamiento_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alojamientos_idalojamiento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alojamientos_idalojamiento_seq OWNER TO postgres;

--
-- TOC entry 5383 (class 0 OID 0)
-- Dependencies: 260
-- Name: alojamientos_idalojamiento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alojamientos_idalojamiento_seq OWNED BY public.alojamientos.idalojamiento;


--
-- TOC entry 249 (class 1259 OID 23839)
-- Name: asistentes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asistentes (
    idasistente integer NOT NULL,
    nombre character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    telefono character varying(20),
    tipoasistente character varying(15) DEFAULT 'General'::character varying NOT NULL,
    CONSTRAINT asistentes_tipoasistente_check CHECK (((tipoasistente)::text = ANY ((ARRAY['General'::character varying, 'Prensa'::character varying, 'Industria'::character varying, 'VIP'::character varying, 'Jurado'::character varying])::text[])))
);


ALTER TABLE public.asistentes OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 23838)
-- Name: asistentes_idasistente_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asistentes_idasistente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asistentes_idasistente_seq OWNER TO postgres;

--
-- TOC entry 5384 (class 0 OID 0)
-- Dependencies: 248
-- Name: asistentes_idasistente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asistentes_idasistente_seq OWNED BY public.asistentes.idasistente;


--
-- TOC entry 239 (class 1259 OID 23732)
-- Name: categorias; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categorias (
    idcategoria integer NOT NULL,
    nombrecategoria character varying(80) NOT NULL,
    descripcion character varying(200)
);


ALTER TABLE public.categorias OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 23731)
-- Name: categorias_idcategoria_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categorias_idcategoria_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categorias_idcategoria_seq OWNER TO postgres;

--
-- TOC entry 5385 (class 0 OID 0)
-- Dependencies: 238
-- Name: categorias_idcategoria_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categorias_idcategoria_seq OWNED BY public.categorias.idcategoria;


--
-- TOC entry 243 (class 1259 OID 23766)
-- Name: competenciapelicula; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.competenciapelicula (
    idpelicula integer NOT NULL,
    idcategoria integer NOT NULL
);


ALTER TABLE public.competenciapelicula OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 23623)
-- Name: ediciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ediciones (
    idedicion integer NOT NULL,
    anio integer NOT NULL,
    nombreedicion character varying(100),
    fechainicio date NOT NULL,
    fechafin date NOT NULL,
    CONSTRAINT ck_edi_fechas CHECK ((fechafin > fechainicio))
);


ALTER TABLE public.ediciones OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 23622)
-- Name: ediciones_idedicion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ediciones_idedicion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ediciones_idedicion_seq OWNER TO postgres;

--
-- TOC entry 5386 (class 0 OID 0)
-- Dependencies: 227
-- Name: ediciones_idedicion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ediciones_idedicion_seq OWNED BY public.ediciones.idedicion;


--
-- TOC entry 253 (class 1259 OID 23865)
-- Name: entradas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.entradas (
    identrada integer NOT NULL,
    idasistente integer NOT NULL,
    idproyeccion integer,
    idevento integer,
    idtarifa integer NOT NULL,
    fechacompra timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_ent_destino CHECK ((((idproyeccion IS NOT NULL) AND (idevento IS NULL)) OR ((idproyeccion IS NULL) AND (idevento IS NOT NULL))))
);


ALTER TABLE public.entradas OWNER TO postgres;

--
-- TOC entry 252 (class 1259 OID 23864)
-- Name: entradas_identrada_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.entradas_identrada_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.entradas_identrada_seq OWNER TO postgres;

--
-- TOC entry 5387 (class 0 OID 0)
-- Dependencies: 252
-- Name: entradas_identrada_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.entradas_identrada_seq OWNED BY public.entradas.identrada;


--
-- TOC entry 245 (class 1259 OID 23784)
-- Name: evaluaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.evaluaciones (
    idevaluacion integer NOT NULL,
    idmiembro integer NOT NULL,
    idpelicula integer NOT NULL,
    idcategoria integer NOT NULL,
    puntuacion integer NOT NULL,
    comentario text,
    CONSTRAINT evaluaciones_puntuacion_check CHECK (((puntuacion >= 1) AND (puntuacion <= 10)))
);


ALTER TABLE public.evaluaciones OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 23783)
-- Name: evaluaciones_idevaluacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.evaluaciones_idevaluacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.evaluaciones_idevaluacion_seq OWNER TO postgres;

--
-- TOC entry 5388 (class 0 OID 0)
-- Dependencies: 244
-- Name: evaluaciones_idevaluacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.evaluaciones_idevaluacion_seq OWNED BY public.evaluaciones.idevaluacion;


--
-- TOC entry 236 (class 1259 OID 23693)
-- Name: eventosparalelos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.eventosparalelos (
    idevento integer NOT NULL,
    idedicion integer NOT NULL,
    nombreevento character varying(150) NOT NULL,
    tipoevento character varying(15) NOT NULL,
    fechahora timestamp without time zone NOT NULL,
    aforo integer NOT NULL,
    costoinscripcion numeric(10,2) DEFAULT 0,
    CONSTRAINT eventosparalelos_aforo_check CHECK ((aforo > 0)),
    CONSTRAINT eventosparalelos_costoinscripcion_check CHECK ((costoinscripcion >= (0)::numeric)),
    CONSTRAINT eventosparalelos_tipoevento_check CHECK (((tipoevento)::text = ANY ((ARRAY['Masterclass'::character varying, 'Taller'::character varying, 'Coctel'::character varying])::text[])))
);


ALTER TABLE public.eventosparalelos OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 23692)
-- Name: eventosparalelos_idevento_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.eventosparalelos_idevento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.eventosparalelos_idevento_seq OWNER TO postgres;

--
-- TOC entry 5389 (class 0 OID 0)
-- Dependencies: 235
-- Name: eventosparalelos_idevento_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.eventosparalelos_idevento_seq OWNED BY public.eventosparalelos.idevento;


--
-- TOC entry 237 (class 1259 OID 23714)
-- Name: expositorevento; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.expositorevento (
    idevento integer NOT NULL,
    idpersonal integer NOT NULL
);


ALTER TABLE public.expositorevento OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 23542)
-- Name: generos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.generos (
    idgenero integer NOT NULL,
    nombregenero character varying(30) NOT NULL
);


ALTER TABLE public.generos OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 23541)
-- Name: generos_idgenero_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.generos_idgenero_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.generos_idgenero_seq OWNER TO postgres;

--
-- TOC entry 5390 (class 0 OID 0)
-- Dependencies: 219
-- Name: generos_idgenero_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.generos_idgenero_seq OWNED BY public.generos.idgenero;


--
-- TOC entry 259 (class 1259 OID 23944)
-- Name: hoteles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hoteles (
    idhotel integer NOT NULL,
    nombrehotel character varying(100) NOT NULL,
    direccion character varying(200),
    estrellas integer,
    CONSTRAINT hoteles_estrellas_check CHECK (((estrellas >= 1) AND (estrellas <= 5)))
);


ALTER TABLE public.hoteles OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 23943)
-- Name: hoteles_idhotel_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hoteles_idhotel_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hoteles_idhotel_seq OWNER TO postgres;

--
-- TOC entry 5391 (class 0 OID 0)
-- Dependencies: 258
-- Name: hoteles_idhotel_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hoteles_idhotel_seq OWNED BY public.hoteles.idhotel;


--
-- TOC entry 242 (class 1259 OID 23749)
-- Name: juradocategoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.juradocategoria (
    idmiembro integer NOT NULL,
    idcategoria integer NOT NULL
);


ALTER TABLE public.juradocategoria OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 23741)
-- Name: miembrosjurado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.miembrosjurado (
    idmiembro integer NOT NULL,
    nombre character varying(100) NOT NULL,
    profesion character varying(60),
    pais character varying(60),
    email character varying(100)
);


ALTER TABLE public.miembrosjurado OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 23740)
-- Name: miembrosjurado_idmiembro_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.miembrosjurado_idmiembro_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.miembrosjurado_idmiembro_seq OWNER TO postgres;

--
-- TOC entry 5392 (class 0 OID 0)
-- Dependencies: 240
-- Name: miembrosjurado_idmiembro_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.miembrosjurado_idmiembro_seq OWNED BY public.miembrosjurado.idmiembro;


--
-- TOC entry 265 (class 1259 OID 24009)
-- Name: patrocinadores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patrocinadores (
    idpatrocinador integer NOT NULL,
    nombreempresa character varying(100) NOT NULL,
    contacto character varying(100),
    email character varying(100),
    redessociales character varying(150)
);


ALTER TABLE public.patrocinadores OWNER TO postgres;

--
-- TOC entry 264 (class 1259 OID 24008)
-- Name: patrocinadores_idpatrocinador_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.patrocinadores_idpatrocinador_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patrocinadores_idpatrocinador_seq OWNER TO postgres;

--
-- TOC entry 5393 (class 0 OID 0)
-- Dependencies: 264
-- Name: patrocinadores_idpatrocinador_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.patrocinadores_idpatrocinador_seq OWNED BY public.patrocinadores.idpatrocinador;


--
-- TOC entry 267 (class 1259 OID 24018)
-- Name: patrocinioedicion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patrocinioedicion (
    idpatrocinio integer NOT NULL,
    idpatrocinador integer NOT NULL,
    idedicion integer NOT NULL,
    tipoaporte character varying(10) NOT NULL,
    monto numeric(12,2),
    descripcionaporte character varying(200),
    CONSTRAINT patrocinioedicion_tipoaporte_check CHECK (((tipoaporte)::text = ANY ((ARRAY['Economico'::character varying, 'Especie'::character varying])::text[])))
);


ALTER TABLE public.patrocinioedicion OWNER TO postgres;

--
-- TOC entry 266 (class 1259 OID 24017)
-- Name: patrocinioedicion_idpatrocinio_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.patrocinioedicion_idpatrocinio_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.patrocinioedicion_idpatrocinio_seq OWNER TO postgres;

--
-- TOC entry 5394 (class 0 OID 0)
-- Dependencies: 266
-- Name: patrocinioedicion_idpatrocinio_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.patrocinioedicion_idpatrocinio_seq OWNED BY public.patrocinioedicion.idpatrocinio;


--
-- TOC entry 223 (class 1259 OID 23575)
-- Name: peliculagenero; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.peliculagenero (
    idpelicula integer NOT NULL,
    idgenero integer NOT NULL
);


ALTER TABLE public.peliculagenero OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 23553)
-- Name: peliculas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.peliculas (
    idpelicula integer NOT NULL,
    titulo character varying(150) NOT NULL,
    anioprod integer NOT NULL,
    duracion integer NOT NULL,
    paisorigen character varying(60) NOT NULL,
    sinopsis text,
    clasificacion character varying(10) NOT NULL,
    formato character varying(10) NOT NULL,
    estado character varying(15) DEFAULT 'Postulada'::character varying NOT NULL,
    CONSTRAINT peliculas_anioprod_check CHECK ((anioprod > 1888)),
    CONSTRAINT peliculas_clasificacion_check CHECK (((clasificacion)::text = ANY ((ARRAY['G'::character varying, 'PG'::character varying, 'PG-13'::character varying, 'R'::character varying, 'NC-17'::character varying, 'ATP'::character varying])::text[]))),
    CONSTRAINT peliculas_duracion_check CHECK ((duracion > 0)),
    CONSTRAINT peliculas_estado_check CHECK (((estado)::text = ANY ((ARRAY['Postulada'::character varying, 'Seleccionada'::character varying, 'Rechazada'::character varying, 'Premiada'::character varying])::text[]))),
    CONSTRAINT peliculas_formato_check CHECK (((formato)::text = ANY ((ARRAY['Digital'::character varying, '35mm'::character varying, 'IMAX'::character varying])::text[])))
);


ALTER TABLE public.peliculas OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 23552)
-- Name: peliculas_idpelicula_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.peliculas_idpelicula_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.peliculas_idpelicula_seq OWNER TO postgres;

--
-- TOC entry 5395 (class 0 OID 0)
-- Dependencies: 221
-- Name: peliculas_idpelicula_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.peliculas_idpelicula_seq OWNED BY public.peliculas.idpelicula;


--
-- TOC entry 225 (class 1259 OID 23593)
-- Name: personal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.personal (
    idpersonal integer NOT NULL,
    nombre character varying(100) NOT NULL,
    biografia text,
    email character varying(100),
    telefono character varying(20),
    nacionalidad character varying(60)
);


ALTER TABLE public.personal OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 23592)
-- Name: personal_idpersonal_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.personal_idpersonal_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.personal_idpersonal_seq OWNER TO postgres;

--
-- TOC entry 5396 (class 0 OID 0)
-- Dependencies: 224
-- Name: personal_idpersonal_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.personal_idpersonal_seq OWNED BY public.personal.idpersonal;


--
-- TOC entry 247 (class 1259 OID 23811)
-- Name: premios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.premios (
    idpremio integer NOT NULL,
    idcategoria integer NOT NULL,
    idpelicula integer NOT NULL,
    idedicion integer NOT NULL
);


ALTER TABLE public.premios OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 23810)
-- Name: premios_idpremio_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.premios_idpremio_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.premios_idpremio_seq OWNER TO postgres;

--
-- TOC entry 5397 (class 0 OID 0)
-- Dependencies: 246
-- Name: premios_idpremio_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.premios_idpremio_seq OWNED BY public.premios.idpremio;


--
-- TOC entry 234 (class 1259 OID 23663)
-- Name: proyecciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proyecciones (
    idproyeccion integer NOT NULL,
    idpelicula integer NOT NULL,
    idsala integer NOT NULL,
    idedicion integer NOT NULL,
    fechahora timestamp without time zone NOT NULL,
    tieneqa boolean DEFAULT false,
    aforodisponible integer NOT NULL,
    CONSTRAINT proyecciones_aforodisponible_check CHECK ((aforodisponible >= 0))
);


ALTER TABLE public.proyecciones OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 23662)
-- Name: proyecciones_idproyeccion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.proyecciones_idproyeccion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.proyecciones_idproyeccion_seq OWNER TO postgres;

--
-- TOC entry 5398 (class 0 OID 0)
-- Dependencies: 233
-- Name: proyecciones_idproyeccion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.proyecciones_idproyeccion_seq OWNED BY public.proyecciones.idproyeccion;


--
-- TOC entry 226 (class 1259 OID 23603)
-- Name: rolespelicula; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rolespelicula (
    idpersonal integer NOT NULL,
    idpelicula integer NOT NULL,
    rol character varying(20) NOT NULL,
    CONSTRAINT rolespelicula_rol_check CHECK (((rol)::text = ANY ((ARRAY['Director'::character varying, 'Actor'::character varying, 'Guionista'::character varying, 'Productor'::character varying])::text[])))
);


ALTER TABLE public.rolespelicula OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 23646)
-- Name: salas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.salas (
    idsala integer NOT NULL,
    nombresala character varying(60) NOT NULL,
    capacidad integer NOT NULL,
    idsede integer NOT NULL,
    CONSTRAINT salas_capacidad_check CHECK ((capacidad > 0))
);


ALTER TABLE public.salas OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 23645)
-- Name: salas_idsala_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.salas_idsala_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.salas_idsala_seq OWNER TO postgres;

--
-- TOC entry 5399 (class 0 OID 0)
-- Dependencies: 231
-- Name: salas_idsala_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.salas_idsala_seq OWNED BY public.salas.idsala;


--
-- TOC entry 230 (class 1259 OID 23637)
-- Name: sedes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sedes (
    idsede integer NOT NULL,
    nombresede character varying(100) NOT NULL,
    direccion character varying(200),
    ciudad character varying(60),
    sitioweb character varying(100)
);


ALTER TABLE public.sedes OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 23636)
-- Name: sedes_idsede_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sedes_idsede_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sedes_idsede_seq OWNER TO postgres;

--
-- TOC entry 5400 (class 0 OID 0)
-- Dependencies: 229
-- Name: sedes_idsede_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sedes_idsede_seq OWNED BY public.sedes.idsede;


--
-- TOC entry 251 (class 1259 OID 23854)
-- Name: tarifas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tarifas (
    idtarifa integer NOT NULL,
    nombretarifa character varying(30) NOT NULL,
    precio numeric(10,2) NOT NULL,
    CONSTRAINT tarifas_precio_check CHECK ((precio >= (0)::numeric))
);


ALTER TABLE public.tarifas OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 23853)
-- Name: tarifas_idtarifa_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tarifas_idtarifa_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tarifas_idtarifa_seq OWNER TO postgres;

--
-- TOC entry 5401 (class 0 OID 0)
-- Dependencies: 250
-- Name: tarifas_idtarifa_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tarifas_idtarifa_seq OWNED BY public.tarifas.idtarifa;


--
-- TOC entry 255 (class 1259 OID 23900)
-- Name: tiposabono; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tiposabono (
    idtipoabono integer NOT NULL,
    nombreabono character varying(60) NOT NULL,
    descripcion character varying(200),
    precio numeric(10,2) NOT NULL,
    CONSTRAINT tiposabono_precio_check CHECK ((precio >= (0)::numeric))
);


ALTER TABLE public.tiposabono OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 23899)
-- Name: tiposabono_idtipoabono_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tiposabono_idtipoabono_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tiposabono_idtipoabono_seq OWNER TO postgres;

--
-- TOC entry 5402 (class 0 OID 0)
-- Dependencies: 254
-- Name: tiposabono_idtipoabono_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tiposabono_idtipoabono_seq OWNED BY public.tiposabono.idtipoabono;


--
-- TOC entry 263 (class 1259 OID 23984)
-- Name: traslados; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.traslados (
    idtraslado integer NOT NULL,
    idpersonal integer NOT NULL,
    idedicion integer NOT NULL,
    tipotraslado character varying(10) NOT NULL,
    origen character varying(100) NOT NULL,
    destino character varying(100) NOT NULL,
    fechahora timestamp without time zone NOT NULL,
    nrovuelo character varying(20),
    CONSTRAINT traslados_tipotraslado_check CHECK (((tipotraslado)::text = ANY ((ARRAY['Vuelo'::character varying, 'Transfer'::character varying])::text[])))
);


ALTER TABLE public.traslados OWNER TO postgres;

--
-- TOC entry 262 (class 1259 OID 23983)
-- Name: traslados_idtraslado_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.traslados_idtraslado_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.traslados_idtraslado_seq OWNER TO postgres;

--
-- TOC entry 5403 (class 0 OID 0)
-- Dependencies: 262
-- Name: traslados_idtraslado_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.traslados_idtraslado_seq OWNED BY public.traslados.idtraslado;


--
-- TOC entry 271 (class 1259 OID 24055)
-- Name: vw_asistentes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_asistentes AS
 SELECT idasistente,
    nombre,
    email,
    tipoasistente
   FROM public.asistentes;


ALTER VIEW public.vw_asistentes OWNER TO postgres;

--
-- TOC entry 274 (class 1259 OID 24067)
-- Name: vw_eventos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_eventos AS
SELECT
    NULL::integer AS idevento,
    NULL::integer AS idedicion,
    NULL::character varying(150) AS nombreevento,
    NULL::character varying(15) AS tipoevento,
    NULL::timestamp without time zone AS fechahora,
    NULL::integer AS aforo,
    NULL::numeric(10,2) AS costoinscripcion,
    NULL::text AS expositores;


ALTER VIEW public.vw_eventos OWNER TO postgres;

--
-- TOC entry 268 (class 1259 OID 24041)
-- Name: vw_peliculas; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_peliculas AS
SELECT
    NULL::integer AS idpelicula,
    NULL::character varying(150) AS titulo,
    NULL::integer AS anioprod,
    NULL::integer AS duracion,
    NULL::character varying(60) AS paisorigen,
    NULL::character varying(10) AS clasificacion,
    NULL::character varying(10) AS formato,
    NULL::character varying(15) AS estado,
    NULL::text AS generos;


ALTER VIEW public.vw_peliculas OWNER TO postgres;

--
-- TOC entry 269 (class 1259 OID 24046)
-- Name: vw_proyecciones; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_proyecciones AS
 SELECT pr.idproyeccion,
    pe.idpelicula,
    pe.titulo,
    pe.duracion,
    sa.idsala,
    sa.nombresala,
    se.nombresede,
    pr.fechahora,
    pr.aforodisponible,
    sa.capacidad,
    pr.tieneqa,
    pr.idedicion
   FROM (((public.proyecciones pr
     JOIN public.peliculas pe ON ((pe.idpelicula = pr.idpelicula)))
     JOIN public.salas sa ON ((sa.idsala = pr.idsala)))
     JOIN public.sedes se ON ((se.idsede = sa.idsede)))
  ORDER BY pr.fechahora;


ALTER VIEW public.vw_proyecciones OWNER TO postgres;

--
-- TOC entry 273 (class 1259 OID 24063)
-- Name: vw_salas; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_salas AS
 SELECT sa.idsala,
    sa.nombresala,
    sa.capacidad,
    se.idsede,
    se.nombresede
   FROM (public.salas sa
     JOIN public.sedes se ON ((se.idsede = sa.idsede)));


ALTER VIEW public.vw_salas OWNER TO postgres;

--
-- TOC entry 270 (class 1259 OID 24051)
-- Name: vw_tarifas; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_tarifas AS
 SELECT idtarifa,
    nombretarifa,
    precio
   FROM public.tarifas
  ORDER BY precio DESC;


ALTER VIEW public.vw_tarifas OWNER TO postgres;

--
-- TOC entry 272 (class 1259 OID 24059)
-- Name: vw_tiposabono; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_tiposabono AS
 SELECT idtipoabono,
    nombreabono,
    descripcion,
    precio
   FROM public.tiposabono;


ALTER VIEW public.vw_tiposabono OWNER TO postgres;

--
-- TOC entry 5040 (class 2604 OID 23914)
-- Name: abonos idabono; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.abonos ALTER COLUMN idabono SET DEFAULT nextval('public.abonos_idabono_seq'::regclass);


--
-- TOC entry 5044 (class 2604 OID 23957)
-- Name: alojamientos idalojamiento; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alojamientos ALTER COLUMN idalojamiento SET DEFAULT nextval('public.alojamientos_idalojamiento_seq'::regclass);


--
-- TOC entry 5034 (class 2604 OID 23842)
-- Name: asistentes idasistente; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asistentes ALTER COLUMN idasistente SET DEFAULT nextval('public.asistentes_idasistente_seq'::regclass);


--
-- TOC entry 5030 (class 2604 OID 23735)
-- Name: categorias idcategoria; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categorias ALTER COLUMN idcategoria SET DEFAULT nextval('public.categorias_idcategoria_seq'::regclass);


--
-- TOC entry 5023 (class 2604 OID 23626)
-- Name: ediciones idedicion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ediciones ALTER COLUMN idedicion SET DEFAULT nextval('public.ediciones_idedicion_seq'::regclass);


--
-- TOC entry 5037 (class 2604 OID 23868)
-- Name: entradas identrada; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entradas ALTER COLUMN identrada SET DEFAULT nextval('public.entradas_identrada_seq'::regclass);


--
-- TOC entry 5032 (class 2604 OID 23787)
-- Name: evaluaciones idevaluacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluaciones ALTER COLUMN idevaluacion SET DEFAULT nextval('public.evaluaciones_idevaluacion_seq'::regclass);


--
-- TOC entry 5028 (class 2604 OID 23696)
-- Name: eventosparalelos idevento; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventosparalelos ALTER COLUMN idevento SET DEFAULT nextval('public.eventosparalelos_idevento_seq'::regclass);


--
-- TOC entry 5019 (class 2604 OID 23545)
-- Name: generos idgenero; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generos ALTER COLUMN idgenero SET DEFAULT nextval('public.generos_idgenero_seq'::regclass);


--
-- TOC entry 5043 (class 2604 OID 23947)
-- Name: hoteles idhotel; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hoteles ALTER COLUMN idhotel SET DEFAULT nextval('public.hoteles_idhotel_seq'::regclass);


--
-- TOC entry 5031 (class 2604 OID 23744)
-- Name: miembrosjurado idmiembro; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.miembrosjurado ALTER COLUMN idmiembro SET DEFAULT nextval('public.miembrosjurado_idmiembro_seq'::regclass);


--
-- TOC entry 5046 (class 2604 OID 24012)
-- Name: patrocinadores idpatrocinador; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patrocinadores ALTER COLUMN idpatrocinador SET DEFAULT nextval('public.patrocinadores_idpatrocinador_seq'::regclass);


--
-- TOC entry 5047 (class 2604 OID 24021)
-- Name: patrocinioedicion idpatrocinio; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patrocinioedicion ALTER COLUMN idpatrocinio SET DEFAULT nextval('public.patrocinioedicion_idpatrocinio_seq'::regclass);


--
-- TOC entry 5020 (class 2604 OID 23556)
-- Name: peliculas idpelicula; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.peliculas ALTER COLUMN idpelicula SET DEFAULT nextval('public.peliculas_idpelicula_seq'::regclass);


--
-- TOC entry 5022 (class 2604 OID 23596)
-- Name: personal idpersonal; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personal ALTER COLUMN idpersonal SET DEFAULT nextval('public.personal_idpersonal_seq'::regclass);


--
-- TOC entry 5033 (class 2604 OID 23814)
-- Name: premios idpremio; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.premios ALTER COLUMN idpremio SET DEFAULT nextval('public.premios_idpremio_seq'::regclass);


--
-- TOC entry 5026 (class 2604 OID 23666)
-- Name: proyecciones idproyeccion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyecciones ALTER COLUMN idproyeccion SET DEFAULT nextval('public.proyecciones_idproyeccion_seq'::regclass);


--
-- TOC entry 5025 (class 2604 OID 23649)
-- Name: salas idsala; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salas ALTER COLUMN idsala SET DEFAULT nextval('public.salas_idsala_seq'::regclass);


--
-- TOC entry 5024 (class 2604 OID 23640)
-- Name: sedes idsede; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sedes ALTER COLUMN idsede SET DEFAULT nextval('public.sedes_idsede_seq'::regclass);


--
-- TOC entry 5036 (class 2604 OID 23857)
-- Name: tarifas idtarifa; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tarifas ALTER COLUMN idtarifa SET DEFAULT nextval('public.tarifas_idtarifa_seq'::regclass);


--
-- TOC entry 5039 (class 2604 OID 23903)
-- Name: tiposabono idtipoabono; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tiposabono ALTER COLUMN idtipoabono SET DEFAULT nextval('public.tiposabono_idtipoabono_seq'::regclass);


--
-- TOC entry 5045 (class 2604 OID 23987)
-- Name: traslados idtraslado; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.traslados ALTER COLUMN idtraslado SET DEFAULT nextval('public.traslados_idtraslado_seq'::regclass);


--
-- TOC entry 5366 (class 0 OID 23911)
-- Dependencies: 257
-- Data for Name: abonos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.abonos (idabono, idasistente, idtipoabono, idedicion, fechacompra, codigoacceso, pagado) FROM stdin;
1	21	1	3	2026-06-03 11:08:24.071395	AB-2026-001	t
2	22	2	3	2026-06-03 11:08:24.071395	AB-2026-002	t
3	6	3	3	2026-06-03 11:08:24.071395	AB-2026-003	t
4	7	3	3	2026-06-03 11:08:24.071395	AB-2026-004	t
5	10	1	3	2026-06-03 11:08:24.071395	AB-2026-005	t
\.


--
-- TOC entry 5370 (class 0 OID 23954)
-- Dependencies: 261
-- Data for Name: alojamientos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alojamientos (idalojamiento, idpersonal, idhotel, idedicion, nrohabitacion, checkin, checkout) FROM stdin;
1	1	1	3	401	2026-06-19	2026-06-27
2	2	2	3	205	2026-06-19	2026-06-27
3	3	1	3	402	2026-06-20	2026-06-26
4	6	3	3	310	2026-06-18	2026-06-28
\.


--
-- TOC entry 5358 (class 0 OID 23839)
-- Dependencies: 249
-- Data for Name: asistentes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.asistentes (idasistente, nombre, email, telefono, tipoasistente) FROM stdin;
1	Juan Pablo Torrez	jptorrez@gmail.com	72000001	General
2	Carla Suarez	csuarez@gmail.com	72000002	General
3	Pedro Flores	pflores@gmail.com	72000003	General
4	Lucia Mendoza	lmendoza@gmail.com	72000004	General
5	Roberto Vaca	rvaca@gmail.com	72000005	General
6	Patricia Guzman	pguzman@gmail.com	72000006	Prensa
7	Carlos Diaz	cdiaz@gmail.com	72000007	Prensa
8	Andres Salinas	asalinas@gmail.com	72000008	General
9	Monica Pereira	mpereira@gmail.com	72000009	General
10	Fernando Castro	fcastro@gmail.com	72000010	Industria
11	Silvana Torres	storres@gmail.com	72000011	VIP
12	Marcos Quispe	mquispe@gmail.com	72000012	General
13	Elena Rodriguez	erodriguez@gmail.com	72000013	General
14	Hugo Alvarado	halvarado@gmail.com	72000014	General
15	Natalia Benitez	nbenitez@gmail.com	72000015	General
16	Gabriel Chavez	gchavez@gmail.com	72000016	General
17	Rosa Mamani	rmamani@gmail.com	72000017	General
18	Sebastian Lopez	slopez@gmail.com	72000018	General
19	Daniela Pinto	dpinto@gmail.com	72000019	Jurado
20	Oscar Medina	omedina@gmail.com	72000020	General
21	Valeria Nunez	vnunez@gmail.com	72000021	Industria
22	Tomas Arce	tarce@gmail.com	72000022	General
\.


--
-- TOC entry 5348 (class 0 OID 23732)
-- Dependencies: 239
-- Data for Name: categorias; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categorias (idcategoria, nombrecategoria, descripcion) FROM stdin;
1	Mejor Pelicula	La mejor obra del festival en su conjunto.
2	Mejor Director	La direccion mas destacada del festival.
3	Mejor Cortometraje	Obra de menos de 30 minutos.
4	Premio del Publico	Votado por los asistentes al festival.
5	Mejor Documental	La mejor obra de no ficcion.
\.


--
-- TOC entry 5352 (class 0 OID 23766)
-- Dependencies: 243
-- Data for Name: competenciapelicula; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.competenciapelicula (idpelicula, idcategoria) FROM stdin;
1	1
2	1
3	1
4	1
1	2
3	2
4	5
2	5
6	3
1	4
2	4
3	4
\.


--
-- TOC entry 5337 (class 0 OID 23623)
-- Dependencies: 228
-- Data for Name: ediciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ediciones (idedicion, anio, nombreedicion, fechainicio, fechafin) FROM stdin;
1	2024	FestCine 2024 - I Edicion	2024-06-15	2024-06-22
2	2025	FestCine 2025 - II Edicion	2025-06-14	2025-06-21
3	2026	FestCine 2026 - III Edicion	2026-06-20	2026-06-27
\.


--
-- TOC entry 5362 (class 0 OID 23865)
-- Dependencies: 253
-- Data for Name: entradas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.entradas (identrada, idasistente, idproyeccion, idevento, idtarifa, fechacompra) FROM stdin;
1	1	1	\N	1	2026-06-03 11:08:24.061429
2	2	1	\N	1	2026-06-03 11:08:24.061429
3	3	1	\N	2	2026-06-03 11:08:24.061429
4	4	2	\N	2	2026-06-03 11:08:24.061429
5	5	2	\N	1	2026-06-03 11:08:24.061429
6	6	2	\N	4	2026-06-03 11:08:24.061429
7	7	3	\N	4	2026-06-03 11:08:24.061429
8	8	3	\N	1	2026-06-03 11:08:24.061429
9	9	3	\N	1	2026-06-03 11:08:24.061429
10	10	4	\N	4	2026-06-03 11:08:24.061429
11	11	4	\N	4	2026-06-03 11:08:24.061429
12	12	4	\N	1	2026-06-03 11:08:24.061429
13	13	5	\N	2	2026-06-03 11:08:24.061429
14	14	5	\N	1	2026-06-03 11:08:24.061429
15	15	5	\N	3	2026-06-03 11:08:24.061429
16	16	6	\N	2	2026-06-03 11:08:24.061429
17	17	6	\N	1	2026-06-03 11:08:24.061429
18	18	6	\N	1	2026-06-03 11:08:24.061429
19	19	7	\N	4	2026-06-03 11:08:24.061429
20	20	7	\N	1	2026-06-03 11:08:24.061429
21	8	\N	1	4	2026-06-03 11:08:24.066988
22	9	\N	2	1	2026-06-03 11:08:24.066988
23	10	\N	2	4	2026-06-03 11:08:24.066988
\.


--
-- TOC entry 5354 (class 0 OID 23784)
-- Dependencies: 245
-- Data for Name: evaluaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.evaluaciones (idevaluacion, idmiembro, idpelicula, idcategoria, puntuacion, comentario) FROM stdin;
1	1	1	1	9	Narrativa impecable y actuaciones sublimes.
2	1	2	1	7	Buena historia, ritmo algo lento.
3	1	3	1	8	Visualmente deslumbrante.
4	1	4	1	6	Correcto pero sin grandes sorpresas.
5	2	1	1	8	Gran direccion de actores.
6	2	2	1	9	Conmovedora y necesaria.
7	2	3	1	7	Ambiciosa aunque irregular.
8	2	4	1	8	Documental honesto y revelador.
9	3	1	1	7	Solida propuesta cinematografica.
10	3	2	1	8	Emotiva y bien construida.
11	3	3	1	9	Ciencia ficcion con alma.
12	3	4	1	6	Tema importante, ejecucion regular.
13	1	1	2	9	Direccion magistral.
14	1	3	2	8	Gran control del ritmo.
15	4	1	2	8	Domina los espacios con maestria.
16	4	3	2	9	Referencia del cine de genero.
17	2	6	3	10	Animacion que supera expectativas.
18	5	6	3	9	Original y poetico.
19	3	1	4	8	El publico la ama.
20	3	2	4	7	Emotiva y accesible.
21	3	3	4	9	Espectacular experiencia.
22	4	4	5	8	Documental necesario.
23	4	2	5	9	Profundo y bien investigado.
24	5	4	5	7	Solido aunque predecible.
25	5	2	5	8	Emotivo y revelador.
\.


--
-- TOC entry 5345 (class 0 OID 23693)
-- Dependencies: 236
-- Data for Name: eventosparalelos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.eventosparalelos (idevento, idedicion, nombreevento, tipoevento, fechahora, aforo, costoinscripcion) FROM stdin;
1	3	Masterclass: Narrativa Visual en el Cine Latinoamericano	Masterclass	2026-06-21 10:00:00	50	0.00
2	3	Taller: Guion para Cine Independiente	Taller	2026-06-22 09:00:00	30	50.00
3	3	Coctel de Inauguracion FestCine 2026	Coctel	2026-06-20 21:00:00	100	0.00
4	3	Taller: Direccion de Actores	Taller	2026-06-23 10:00:00	25	80.00
\.


--
-- TOC entry 5346 (class 0 OID 23714)
-- Dependencies: 237
-- Data for Name: expositorevento; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.expositorevento (idevento, idpersonal) FROM stdin;
1	1
1	2
2	4
3	5
4	1
\.


--
-- TOC entry 5329 (class 0 OID 23542)
-- Dependencies: 220
-- Data for Name: generos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.generos (idgenero, nombregenero) FROM stdin;
1	Drama
2	Sci-Fi
3	Documental
4	Thriller
5	Comedia
6	Animacion
\.


--
-- TOC entry 5368 (class 0 OID 23944)
-- Dependencies: 259
-- Data for Name: hoteles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hoteles (idhotel, nombrehotel, direccion, estrellas) FROM stdin;
1	Los Tajibos Hotel	Av. San Martin 455, Santa Cruz	5
2	Hotel Cortez	Av. Cristobal de Mendoza 280	4
3	Marriott Santa Cruz	Av. San Martin 1700	5
\.


--
-- TOC entry 5351 (class 0 OID 23749)
-- Dependencies: 242
-- Data for Name: juradocategoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.juradocategoria (idmiembro, idcategoria) FROM stdin;
1	1
1	2
2	1
2	3
3	1
3	4
4	2
4	5
5	3
5	5
\.


--
-- TOC entry 5350 (class 0 OID 23741)
-- Dependencies: 241
-- Data for Name: miembrosjurado; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.miembrosjurado (idmiembro, nombre, profesion, pais, email) FROM stdin;
1	Roberto Calderon	Critico de Cine	Espana	rcalderon@critica.es
2	Isabel Vargas	Directora de Cine	Argentina	ivargas@cine.ar
3	Michael Brown	Productor	USA	mbrown@films.us
4	Claudia Mendez	Periodista Cultural	Mexico	cmendez@cultura.mx
5	Remy Fontaine	Director de Festival	Francia	rfontaine@festival.fr
\.


--
-- TOC entry 5374 (class 0 OID 24009)
-- Dependencies: 265
-- Data for Name: patrocinadores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.patrocinadores (idpatrocinador, nombreempresa, contacto, email, redessociales) FROM stdin;
1	Banco Union	Lic. Patricia Heredia	pheredia@bancounion.com.bo	@bancounionbo
2	YPFB	Ing. Carlos Morales	cmorales@ypfb.com.bo	@ypfboficial
3	Tigo Bolivia	Lic. Andres Vidal	avidal@tigo.com.bo	@tigobolivia
4	Cerveceria Boliviana	Sr. Pedro Roca	proca@cbba.com.bo	@cbbaoficial
\.


--
-- TOC entry 5376 (class 0 OID 24018)
-- Dependencies: 267
-- Data for Name: patrocinioedicion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.patrocinioedicion (idpatrocinio, idpatrocinador, idedicion, tipoaporte, monto, descripcionaporte) FROM stdin;
1	1	1	Economico	50000.00	Patrocinio principal I edicion
2	2	1	Especie	\N	Logistica de combustible
3	1	2	Economico	60000.00	Patrocinio principal II edicion
4	3	2	Economico	20000.00	Patrocinio tecnologia
5	1	3	Economico	75000.00	Patrocinio principal III edicion
6	2	3	Economico	30000.00	Patrocinio energia
7	3	3	Especie	\N	Conectividad del evento
8	4	3	Especie	\N	Bebidas para eventos
\.


--
-- TOC entry 5332 (class 0 OID 23575)
-- Dependencies: 223
-- Data for Name: peliculagenero; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.peliculagenero (idpelicula, idgenero) FROM stdin;
1	1
1	4
2	1
2	3
3	2
3	4
4	3
5	1
5	6
6	6
7	4
\.


--
-- TOC entry 5331 (class 0 OID 23553)
-- Dependencies: 222
-- Data for Name: peliculas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.peliculas (idpelicula, titulo, anioprod, duracion, paisorigen, sinopsis, clasificacion, formato, estado) FROM stdin;
1	El Ultimo Tren del Sur	2024	112	Argentina	Un viaje ferroviario que cambia la vida de sus pasajeros.	PG	Digital	Seleccionada
2	Memoria de Cenizas	2023	98	Bolivia	Un anciano busca recuperar su historia antes de morir.	PG-13	Digital	Seleccionada
3	Mas Alla del Horizonte	2024	134	Mexico	Una mision espacial enfrenta el dilema de volver a casa.	PG-13	IMAX	Seleccionada
4	La Sal de la Tierra	2023	87	Colombia	Documental sobre comunidades afrodescendientes del Pacifico.	ATP	35mm	Seleccionada
5	Ruido Blanco	2024	105	Chile	Un compositor pierde el oido y busca otra forma de crear.	PG	Digital	Seleccionada
6	El Jardin de los Suenos	2023	76	Peru	Animacion que explora el inconsciente colectivo andino.	ATP	Digital	Premiada
7	Codigo Rojo	2024	118	Brasil	Thriller politico en los pasillos del poder latinoamericano.	R	Digital	Seleccionada
\.


--
-- TOC entry 5334 (class 0 OID 23593)
-- Dependencies: 225
-- Data for Name: personal; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.personal (idpersonal, nombre, biografia, email, telefono, nacionalidad) FROM stdin;
1	Maria Fernanda Rios	Directora argentina premiada en Sundance.	mfrios@cine.ar	+54911000001	Argentina
2	Jorge Luis Mamani	Director boliviano, documental y ficcion.	jmamani@cine.bo	+59176000002	Bolivia
3	Valentina Cruz	Actriz mexicana con 15 anos de trayectoria.	vcruz@cine.mx	+52155000003	Mexico
4	Carlos Herrera	Guionista colombiano, especialista en documental.	cherrera@cine.co	+57310000004	Colombia
5	Ana Sofia Delgado	Productora chilena, 10 filmes internacionales.	asdelgado@cine.cl	+56992000005	Chile
6	Diego Ramos	Actor y director peruano, cine de animacion.	dramos@cine.pe	+51987000006	Peru
7	Luisa Montoya	Actriz brasilena, teatro y cine.	lmontoya@cine.br	+55119000007	Brasil
8	Fernando Quiroga	Director de fotografia, Bolivia.	fquiroga@cine.bo	+59172000008	Bolivia
\.


--
-- TOC entry 5356 (class 0 OID 23811)
-- Dependencies: 247
-- Data for Name: premios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.premios (idpremio, idcategoria, idpelicula, idedicion) FROM stdin;
1	1	2	3
2	2	3	3
3	3	6	3
4	5	2	3
\.


--
-- TOC entry 5343 (class 0 OID 23663)
-- Dependencies: 234
-- Data for Name: proyecciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.proyecciones (idproyeccion, idpelicula, idsala, idedicion, fechahora, tieneqa, aforodisponible) FROM stdin;
1	1	1	3	2026-06-20 19:00:00	t	120
2	2	2	3	2026-06-20 20:00:00	f	80
3	3	3	3	2026-06-21 18:00:00	t	200
4	4	4	3	2026-06-21 20:30:00	f	60
5	5	5	3	2026-06-22 19:00:00	f	150
6	6	6	3	2026-06-22 17:00:00	t	90
7	7	1	3	2026-06-23 21:00:00	f	120
8	1	3	3	2026-06-24 19:00:00	f	200
9	3	5	3	2026-06-24 21:00:00	t	150
10	2	6	3	2026-06-25 18:30:00	f	90
11	5	2	3	2026-06-25 20:00:00	t	80
12	6	4	3	2026-06-26 17:00:00	f	60
\.


--
-- TOC entry 5335 (class 0 OID 23603)
-- Dependencies: 226
-- Data for Name: rolespelicula; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rolespelicula (idpersonal, idpelicula, rol) FROM stdin;
1	1	Director
3	1	Actor
2	2	Director
2	2	Guionista
3	3	Actor
5	3	Productor
4	4	Guionista
8	4	Director
5	5	Productor
1	5	Director
6	6	Director
6	6	Actor
7	7	Actor
4	7	Guionista
\.


--
-- TOC entry 5341 (class 0 OID 23646)
-- Dependencies: 232
-- Data for Name: salas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.salas (idsala, nombresala, capacidad, idsede) FROM stdin;
1	Sala Lumiere	120	1
2	Sala Eisenstein	80	1
3	Sala Principal	200	2
4	Sala Municipal	60	2
5	Sala Norte A	150	3
6	Sala Norte B	90	3
\.


--
-- TOC entry 5339 (class 0 OID 23637)
-- Dependencies: 230
-- Data for Name: sedes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sedes (idsede, nombresede, direccion, ciudad, sitioweb) FROM stdin;
1	Cine Centro	Av. Monsenor Rivero 345	Santa Cruz de la Sierra	www.cinecentro.bo
2	Teatro Municipal	Plaza 24 de Septiembre s/n	Santa Cruz de la Sierra	www.teatromunicipal.bo
3	Multicine Norte	Av. Banzer km 5	Santa Cruz de la Sierra	www.multicinorte.bo
\.


--
-- TOC entry 5360 (class 0 OID 23854)
-- Dependencies: 251
-- Data for Name: tarifas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tarifas (idtarifa, nombretarifa, precio) FROM stdin;
1	General	35.00
2	Estudiante	20.00
3	Jubilado	15.00
4	Acreditado	0.00
\.


--
-- TOC entry 5364 (class 0 OID 23900)
-- Dependencies: 255
-- Data for Name: tiposabono; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tiposabono (idtipoabono, nombreabono, descripcion, precio) FROM stdin;
1	Abono Fin de Semana	Acceso ilimitado sabado y domingo.	150.00
2	Abono Total	Acceso a todas las proyecciones.	400.00
3	Abono Prensa	Acceso completo para medios.	0.00
\.


--
-- TOC entry 5372 (class 0 OID 23984)
-- Dependencies: 263
-- Data for Name: traslados; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.traslados (idtraslado, idpersonal, idedicion, tipotraslado, origen, destino, fechahora, nrovuelo) FROM stdin;
1	1	3	Vuelo	Buenos Aires (EZE)	Santa Cruz (VVI)	2026-06-19 08:00:00	LA832
2	2	3	Vuelo	La Paz (LPB)	Santa Cruz (VVI)	2026-06-19 10:30:00	OB101
3	3	3	Vuelo	Ciudad de Mexico	Santa Cruz (VVI)	2026-06-20 06:00:00	AM543
4	6	3	Vuelo	Lima (LIM)	Santa Cruz (VVI)	2026-06-18 14:00:00	LA2081
5	1	3	Transfer	Santa Cruz (VVI)	Los Tajibos Hotel	2026-06-19 11:00:00	\N
\.


--
-- TOC entry 5404 (class 0 OID 0)
-- Dependencies: 256
-- Name: abonos_idabono_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.abonos_idabono_seq', 5, true);


--
-- TOC entry 5405 (class 0 OID 0)
-- Dependencies: 260
-- Name: alojamientos_idalojamiento_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alojamientos_idalojamiento_seq', 4, true);


--
-- TOC entry 5406 (class 0 OID 0)
-- Dependencies: 248
-- Name: asistentes_idasistente_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asistentes_idasistente_seq', 22, true);


--
-- TOC entry 5407 (class 0 OID 0)
-- Dependencies: 238
-- Name: categorias_idcategoria_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categorias_idcategoria_seq', 5, true);


--
-- TOC entry 5408 (class 0 OID 0)
-- Dependencies: 227
-- Name: ediciones_idedicion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.ediciones_idedicion_seq', 3, true);


--
-- TOC entry 5409 (class 0 OID 0)
-- Dependencies: 252
-- Name: entradas_identrada_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.entradas_identrada_seq', 23, true);


--
-- TOC entry 5410 (class 0 OID 0)
-- Dependencies: 244
-- Name: evaluaciones_idevaluacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.evaluaciones_idevaluacion_seq', 25, true);


--
-- TOC entry 5411 (class 0 OID 0)
-- Dependencies: 235
-- Name: eventosparalelos_idevento_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.eventosparalelos_idevento_seq', 4, true);


--
-- TOC entry 5412 (class 0 OID 0)
-- Dependencies: 219
-- Name: generos_idgenero_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.generos_idgenero_seq', 6, true);


--
-- TOC entry 5413 (class 0 OID 0)
-- Dependencies: 258
-- Name: hoteles_idhotel_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.hoteles_idhotel_seq', 3, true);


--
-- TOC entry 5414 (class 0 OID 0)
-- Dependencies: 240
-- Name: miembrosjurado_idmiembro_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.miembrosjurado_idmiembro_seq', 5, true);


--
-- TOC entry 5415 (class 0 OID 0)
-- Dependencies: 264
-- Name: patrocinadores_idpatrocinador_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.patrocinadores_idpatrocinador_seq', 4, true);


--
-- TOC entry 5416 (class 0 OID 0)
-- Dependencies: 266
-- Name: patrocinioedicion_idpatrocinio_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.patrocinioedicion_idpatrocinio_seq', 8, true);


--
-- TOC entry 5417 (class 0 OID 0)
-- Dependencies: 221
-- Name: peliculas_idpelicula_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.peliculas_idpelicula_seq', 7, true);


--
-- TOC entry 5418 (class 0 OID 0)
-- Dependencies: 224
-- Name: personal_idpersonal_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.personal_idpersonal_seq', 8, true);


--
-- TOC entry 5419 (class 0 OID 0)
-- Dependencies: 246
-- Name: premios_idpremio_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.premios_idpremio_seq', 4, true);


--
-- TOC entry 5420 (class 0 OID 0)
-- Dependencies: 233
-- Name: proyecciones_idproyeccion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.proyecciones_idproyeccion_seq', 12, true);


--
-- TOC entry 5421 (class 0 OID 0)
-- Dependencies: 231
-- Name: salas_idsala_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.salas_idsala_seq', 6, true);


--
-- TOC entry 5422 (class 0 OID 0)
-- Dependencies: 229
-- Name: sedes_idsede_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sedes_idsede_seq', 3, true);


--
-- TOC entry 5423 (class 0 OID 0)
-- Dependencies: 250
-- Name: tarifas_idtarifa_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tarifas_idtarifa_seq', 4, true);


--
-- TOC entry 5424 (class 0 OID 0)
-- Dependencies: 254
-- Name: tiposabono_idtipoabono_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tiposabono_idtipoabono_seq', 3, true);


--
-- TOC entry 5425 (class 0 OID 0)
-- Dependencies: 262
-- Name: traslados_idtraslado_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.traslados_idtraslado_seq', 5, true);


--
-- TOC entry 5124 (class 2606 OID 23925)
-- Name: abonos pk_ab; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.abonos
    ADD CONSTRAINT pk_ab PRIMARY KEY (idabono);


--
-- TOC entry 5132 (class 2606 OID 23967)
-- Name: alojamientos pk_aloj; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alojamientos
    ADD CONSTRAINT pk_aloj PRIMARY KEY (idalojamiento);


--
-- TOC entry 5112 (class 2606 OID 23850)
-- Name: asistentes pk_asi; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asistentes
    ADD CONSTRAINT pk_asi PRIMARY KEY (idasistente);


--
-- TOC entry 5096 (class 2606 OID 23739)
-- Name: categorias pk_cat; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT pk_cat PRIMARY KEY (idcategoria);


--
-- TOC entry 5102 (class 2606 OID 23772)
-- Name: competenciapelicula pk_comppel; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competenciapelicula
    ADD CONSTRAINT pk_comppel PRIMARY KEY (idpelicula, idcategoria);


--
-- TOC entry 5082 (class 2606 OID 23633)
-- Name: ediciones pk_edi; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ediciones
    ADD CONSTRAINT pk_edi PRIMARY KEY (idedicion);


--
-- TOC entry 5118 (class 2606 OID 23876)
-- Name: entradas pk_ent; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entradas
    ADD CONSTRAINT pk_ent PRIMARY KEY (identrada);


--
-- TOC entry 5104 (class 2606 OID 23797)
-- Name: evaluaciones pk_eval; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluaciones
    ADD CONSTRAINT pk_eval PRIMARY KEY (idevaluacion);


--
-- TOC entry 5092 (class 2606 OID 23708)
-- Name: eventosparalelos pk_evt; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventosparalelos
    ADD CONSTRAINT pk_evt PRIMARY KEY (idevento);


--
-- TOC entry 5094 (class 2606 OID 23720)
-- Name: expositorevento pk_expevt; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expositorevento
    ADD CONSTRAINT pk_expevt PRIMARY KEY (idevento, idpersonal);


--
-- TOC entry 5070 (class 2606 OID 23549)
-- Name: generos pk_gen; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generos
    ADD CONSTRAINT pk_gen PRIMARY KEY (idgenero);


--
-- TOC entry 5130 (class 2606 OID 23952)
-- Name: hoteles pk_hot; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hoteles
    ADD CONSTRAINT pk_hot PRIMARY KEY (idhotel);


--
-- TOC entry 5100 (class 2606 OID 23755)
-- Name: juradocategoria pk_jurcat; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.juradocategoria
    ADD CONSTRAINT pk_jurcat PRIMARY KEY (idmiembro, idcategoria);


--
-- TOC entry 5098 (class 2606 OID 23748)
-- Name: miembrosjurado pk_mj; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.miembrosjurado
    ADD CONSTRAINT pk_mj PRIMARY KEY (idmiembro);


--
-- TOC entry 5138 (class 2606 OID 24028)
-- Name: patrocinioedicion pk_patedi; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patrocinioedicion
    ADD CONSTRAINT pk_patedi PRIMARY KEY (idpatrocinio);


--
-- TOC entry 5136 (class 2606 OID 24016)
-- Name: patrocinadores pk_patr; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patrocinadores
    ADD CONSTRAINT pk_patr PRIMARY KEY (idpatrocinador);


--
-- TOC entry 5074 (class 2606 OID 23574)
-- Name: peliculas pk_pel; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.peliculas
    ADD CONSTRAINT pk_pel PRIMARY KEY (idpelicula);


--
-- TOC entry 5076 (class 2606 OID 23581)
-- Name: peliculagenero pk_pelgen; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.peliculagenero
    ADD CONSTRAINT pk_pelgen PRIMARY KEY (idpelicula, idgenero);


--
-- TOC entry 5078 (class 2606 OID 23602)
-- Name: personal pk_per; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.personal
    ADD CONSTRAINT pk_per PRIMARY KEY (idpersonal);


--
-- TOC entry 5108 (class 2606 OID 23820)
-- Name: premios pk_pre; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.premios
    ADD CONSTRAINT pk_pre PRIMARY KEY (idpremio);


--
-- TOC entry 5090 (class 2606 OID 23676)
-- Name: proyecciones pk_proy; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyecciones
    ADD CONSTRAINT pk_proy PRIMARY KEY (idproyeccion);


--
-- TOC entry 5080 (class 2606 OID 23611)
-- Name: rolespelicula pk_rolpel; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rolespelicula
    ADD CONSTRAINT pk_rolpel PRIMARY KEY (idpersonal, idpelicula, rol);


--
-- TOC entry 5088 (class 2606 OID 23656)
-- Name: salas pk_sal; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salas
    ADD CONSTRAINT pk_sal PRIMARY KEY (idsala);


--
-- TOC entry 5086 (class 2606 OID 23644)
-- Name: sedes pk_sed; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sedes
    ADD CONSTRAINT pk_sed PRIMARY KEY (idsede);


--
-- TOC entry 5116 (class 2606 OID 23863)
-- Name: tarifas pk_tar; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tarifas
    ADD CONSTRAINT pk_tar PRIMARY KEY (idtarifa);


--
-- TOC entry 5122 (class 2606 OID 23909)
-- Name: tiposabono pk_tipoab; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tiposabono
    ADD CONSTRAINT pk_tipoab PRIMARY KEY (idtipoabono);


--
-- TOC entry 5134 (class 2606 OID 23997)
-- Name: traslados pk_tras; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.traslados
    ADD CONSTRAINT pk_tras PRIMARY KEY (idtraslado);


--
-- TOC entry 5126 (class 2606 OID 24040)
-- Name: abonos uq_ab_asitipo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.abonos
    ADD CONSTRAINT uq_ab_asitipo UNIQUE (idasistente, idtipoabono);


--
-- TOC entry 5128 (class 2606 OID 23927)
-- Name: abonos uq_abcod; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.abonos
    ADD CONSTRAINT uq_abcod UNIQUE (codigoacceso);


--
-- TOC entry 5114 (class 2606 OID 23852)
-- Name: asistentes uq_asiemail; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asistentes
    ADD CONSTRAINT uq_asiemail UNIQUE (email);


--
-- TOC entry 5084 (class 2606 OID 23635)
-- Name: ediciones uq_edianio; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ediciones
    ADD CONSTRAINT uq_edianio UNIQUE (anio);


--
-- TOC entry 5106 (class 2606 OID 23799)
-- Name: evaluaciones uq_eval; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluaciones
    ADD CONSTRAINT uq_eval UNIQUE (idmiembro, idpelicula, idcategoria);


--
-- TOC entry 5072 (class 2606 OID 23551)
-- Name: generos uq_gennom; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.generos
    ADD CONSTRAINT uq_gennom UNIQUE (nombregenero);


--
-- TOC entry 5110 (class 2606 OID 23822)
-- Name: premios uq_precatedi; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.premios
    ADD CONSTRAINT uq_precatedi UNIQUE (idcategoria, idedicion);


--
-- TOC entry 5119 (class 1259 OID 23898)
-- Name: ux_ent_asievt; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_ent_asievt ON public.entradas USING btree (idasistente, idevento) WHERE (idevento IS NOT NULL);


--
-- TOC entry 5120 (class 1259 OID 23897)
-- Name: ux_ent_asiproy; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ux_ent_asiproy ON public.entradas USING btree (idasistente, idproyeccion) WHERE (idproyeccion IS NOT NULL);


--
-- TOC entry 5327 (class 2618 OID 24070)
-- Name: vw_eventos _RETURN; Type: RULE; Schema: public; Owner: postgres
--

CREATE OR REPLACE VIEW public.vw_eventos AS
 SELECT e.idevento,
    e.idedicion,
    e.nombreevento,
    e.tipoevento,
    e.fechahora,
    e.aforo,
    e.costoinscripcion,
    COALESCE(string_agg((p.nombre)::text, ', '::text), ''::text) AS expositores
   FROM ((public.eventosparalelos e
     LEFT JOIN public.expositorevento ee ON ((ee.idevento = e.idevento)))
     LEFT JOIN public.personal p ON ((p.idpersonal = ee.idpersonal)))
  GROUP BY e.idevento
  ORDER BY e.fechahora;


--
-- TOC entry 5321 (class 2618 OID 24044)
-- Name: vw_peliculas _RETURN; Type: RULE; Schema: public; Owner: postgres
--

CREATE OR REPLACE VIEW public.vw_peliculas AS
 SELECT p.idpelicula,
    p.titulo,
    p.anioprod,
    p.duracion,
    p.paisorigen,
    p.clasificacion,
    p.formato,
    p.estado,
    COALESCE(string_agg((g.nombregenero)::text, ', '::text), ''::text) AS generos
   FROM ((public.peliculas p
     LEFT JOIN public.peliculagenero pg ON ((pg.idpelicula = p.idpelicula)))
     LEFT JOIN public.generos g ON ((g.idgenero = pg.idgenero)))
  WHERE ((p.estado)::text = ANY ((ARRAY['Seleccionada'::character varying, 'Premiada'::character varying])::text[]))
  GROUP BY p.idpelicula
  ORDER BY p.titulo;


--
-- TOC entry 5173 (class 2620 OID 24076)
-- Name: proyecciones tr_controlagenda; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_controlagenda BEFORE INSERT OR UPDATE ON public.proyecciones FOR EACH ROW EXECUTE FUNCTION public.fn_controlagenda();


--
-- TOC entry 5163 (class 2606 OID 23928)
-- Name: abonos fk_ab_asi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.abonos
    ADD CONSTRAINT fk_ab_asi FOREIGN KEY (idasistente) REFERENCES public.asistentes(idasistente);


--
-- TOC entry 5164 (class 2606 OID 23938)
-- Name: abonos fk_ab_edi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.abonos
    ADD CONSTRAINT fk_ab_edi FOREIGN KEY (idedicion) REFERENCES public.ediciones(idedicion);


--
-- TOC entry 5165 (class 2606 OID 23933)
-- Name: abonos fk_ab_tipo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.abonos
    ADD CONSTRAINT fk_ab_tipo FOREIGN KEY (idtipoabono) REFERENCES public.tiposabono(idtipoabono);


--
-- TOC entry 5166 (class 2606 OID 23978)
-- Name: alojamientos fk_aloj_edi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alojamientos
    ADD CONSTRAINT fk_aloj_edi FOREIGN KEY (idedicion) REFERENCES public.ediciones(idedicion);


--
-- TOC entry 5167 (class 2606 OID 23973)
-- Name: alojamientos fk_aloj_hot; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alojamientos
    ADD CONSTRAINT fk_aloj_hot FOREIGN KEY (idhotel) REFERENCES public.hoteles(idhotel);


--
-- TOC entry 5168 (class 2606 OID 23968)
-- Name: alojamientos fk_aloj_per; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alojamientos
    ADD CONSTRAINT fk_aloj_per FOREIGN KEY (idpersonal) REFERENCES public.personal(idpersonal);


--
-- TOC entry 5152 (class 2606 OID 23778)
-- Name: competenciapelicula fk_comppel_cat; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competenciapelicula
    ADD CONSTRAINT fk_comppel_cat FOREIGN KEY (idcategoria) REFERENCES public.categorias(idcategoria);


--
-- TOC entry 5153 (class 2606 OID 23773)
-- Name: competenciapelicula fk_comppel_pel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.competenciapelicula
    ADD CONSTRAINT fk_comppel_pel FOREIGN KEY (idpelicula) REFERENCES public.peliculas(idpelicula);


--
-- TOC entry 5159 (class 2606 OID 23877)
-- Name: entradas fk_ent_asi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entradas
    ADD CONSTRAINT fk_ent_asi FOREIGN KEY (idasistente) REFERENCES public.asistentes(idasistente);


--
-- TOC entry 5160 (class 2606 OID 23887)
-- Name: entradas fk_ent_evt; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entradas
    ADD CONSTRAINT fk_ent_evt FOREIGN KEY (idevento) REFERENCES public.eventosparalelos(idevento);


--
-- TOC entry 5161 (class 2606 OID 23882)
-- Name: entradas fk_ent_proy; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entradas
    ADD CONSTRAINT fk_ent_proy FOREIGN KEY (idproyeccion) REFERENCES public.proyecciones(idproyeccion);


--
-- TOC entry 5162 (class 2606 OID 23892)
-- Name: entradas fk_ent_tar; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.entradas
    ADD CONSTRAINT fk_ent_tar FOREIGN KEY (idtarifa) REFERENCES public.tarifas(idtarifa);


--
-- TOC entry 5154 (class 2606 OID 23805)
-- Name: evaluaciones fk_eval_cp; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluaciones
    ADD CONSTRAINT fk_eval_cp FOREIGN KEY (idpelicula, idcategoria) REFERENCES public.competenciapelicula(idpelicula, idcategoria);


--
-- TOC entry 5155 (class 2606 OID 23800)
-- Name: evaluaciones fk_eval_jc; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.evaluaciones
    ADD CONSTRAINT fk_eval_jc FOREIGN KEY (idmiembro, idcategoria) REFERENCES public.juradocategoria(idmiembro, idcategoria);


--
-- TOC entry 5147 (class 2606 OID 23709)
-- Name: eventosparalelos fk_evt_edi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventosparalelos
    ADD CONSTRAINT fk_evt_edi FOREIGN KEY (idedicion) REFERENCES public.ediciones(idedicion);


--
-- TOC entry 5148 (class 2606 OID 23721)
-- Name: expositorevento fk_expevt_evt; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expositorevento
    ADD CONSTRAINT fk_expevt_evt FOREIGN KEY (idevento) REFERENCES public.eventosparalelos(idevento);


--
-- TOC entry 5149 (class 2606 OID 23726)
-- Name: expositorevento fk_expevt_per; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.expositorevento
    ADD CONSTRAINT fk_expevt_per FOREIGN KEY (idpersonal) REFERENCES public.personal(idpersonal);


--
-- TOC entry 5150 (class 2606 OID 23761)
-- Name: juradocategoria fk_jurcat_cat; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.juradocategoria
    ADD CONSTRAINT fk_jurcat_cat FOREIGN KEY (idcategoria) REFERENCES public.categorias(idcategoria);


--
-- TOC entry 5151 (class 2606 OID 23756)
-- Name: juradocategoria fk_jurcat_mj; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.juradocategoria
    ADD CONSTRAINT fk_jurcat_mj FOREIGN KEY (idmiembro) REFERENCES public.miembrosjurado(idmiembro);


--
-- TOC entry 5171 (class 2606 OID 24034)
-- Name: patrocinioedicion fk_patedi_edi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patrocinioedicion
    ADD CONSTRAINT fk_patedi_edi FOREIGN KEY (idedicion) REFERENCES public.ediciones(idedicion);


--
-- TOC entry 5172 (class 2606 OID 24029)
-- Name: patrocinioedicion fk_patedi_pat; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patrocinioedicion
    ADD CONSTRAINT fk_patedi_pat FOREIGN KEY (idpatrocinador) REFERENCES public.patrocinadores(idpatrocinador);


--
-- TOC entry 5139 (class 2606 OID 23587)
-- Name: peliculagenero fk_pelgen_gen; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.peliculagenero
    ADD CONSTRAINT fk_pelgen_gen FOREIGN KEY (idgenero) REFERENCES public.generos(idgenero);


--
-- TOC entry 5140 (class 2606 OID 23582)
-- Name: peliculagenero fk_pelgen_pel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.peliculagenero
    ADD CONSTRAINT fk_pelgen_pel FOREIGN KEY (idpelicula) REFERENCES public.peliculas(idpelicula);


--
-- TOC entry 5156 (class 2606 OID 23823)
-- Name: premios fk_pre_cat; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.premios
    ADD CONSTRAINT fk_pre_cat FOREIGN KEY (idcategoria) REFERENCES public.categorias(idcategoria);


--
-- TOC entry 5157 (class 2606 OID 23833)
-- Name: premios fk_pre_edi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.premios
    ADD CONSTRAINT fk_pre_edi FOREIGN KEY (idedicion) REFERENCES public.ediciones(idedicion);


--
-- TOC entry 5158 (class 2606 OID 23828)
-- Name: premios fk_pre_pel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.premios
    ADD CONSTRAINT fk_pre_pel FOREIGN KEY (idpelicula) REFERENCES public.peliculas(idpelicula);


--
-- TOC entry 5144 (class 2606 OID 23687)
-- Name: proyecciones fk_proy_edi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyecciones
    ADD CONSTRAINT fk_proy_edi FOREIGN KEY (idedicion) REFERENCES public.ediciones(idedicion);


--
-- TOC entry 5145 (class 2606 OID 23677)
-- Name: proyecciones fk_proy_pel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyecciones
    ADD CONSTRAINT fk_proy_pel FOREIGN KEY (idpelicula) REFERENCES public.peliculas(idpelicula);


--
-- TOC entry 5146 (class 2606 OID 23682)
-- Name: proyecciones fk_proy_sal; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proyecciones
    ADD CONSTRAINT fk_proy_sal FOREIGN KEY (idsala) REFERENCES public.salas(idsala);


--
-- TOC entry 5141 (class 2606 OID 23617)
-- Name: rolespelicula fk_rolpel_pel; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rolespelicula
    ADD CONSTRAINT fk_rolpel_pel FOREIGN KEY (idpelicula) REFERENCES public.peliculas(idpelicula);


--
-- TOC entry 5142 (class 2606 OID 23612)
-- Name: rolespelicula fk_rolpel_per; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rolespelicula
    ADD CONSTRAINT fk_rolpel_per FOREIGN KEY (idpersonal) REFERENCES public.personal(idpersonal);


--
-- TOC entry 5143 (class 2606 OID 23657)
-- Name: salas fk_sal_sed; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salas
    ADD CONSTRAINT fk_sal_sed FOREIGN KEY (idsede) REFERENCES public.sedes(idsede);


--
-- TOC entry 5169 (class 2606 OID 24003)
-- Name: traslados fk_tras_edi; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.traslados
    ADD CONSTRAINT fk_tras_edi FOREIGN KEY (idedicion) REFERENCES public.ediciones(idedicion);


--
-- TOC entry 5170 (class 2606 OID 23998)
-- Name: traslados fk_tras_per; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.traslados
    ADD CONSTRAINT fk_tras_per FOREIGN KEY (idpersonal) REFERENCES public.personal(idpersonal);


-- Completed on 2026-06-03 13:20:22

--
-- PostgreSQL database dump complete
--

\unrestrict 6An17p1y3zFpabWAPg8qm7xshqRy8qkUTrWjl2yFyQgFKZTrBKXsWpL70pUGXRK

