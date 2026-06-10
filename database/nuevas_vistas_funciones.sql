/* ============================================================
   FESTCINE - Nuevas Vistas y Funciones
   Rama: jose
   Proposito: Eliminar SQL embebido del backend Python.
   Ejecutar en psql: \i nuevas_vistas_funciones.sql
   ============================================================ */

-- ============================================================
-- PASO 1: Vistas que ya existian en _INIT_SQL de database.py
--         (se mueven aqui, fuera de Python)
-- ============================================================

CREATE OR REPLACE VIEW public.vw_Eventos AS
    SELECT
        ep.idevento          AS IdEvento,
        ep.idedicion         AS IdEdicion,
        ep.nombreevento      AS NombreEvento,
        ep.tipoevento        AS TipoEvento,
        ep.fechahora         AS FechaHora,
        ep.aforo             AS Aforo,
        ep.costoinscripcion  AS CostoInscripcion,
        ed.anio              AS Anio,
        ed.nombreedicion     AS NombreEdicion,
        COALESCE(STRING_AGG(per.nombre, ', ' ORDER BY per.nombre), '') AS Expositores
    FROM public.eventosparalelos ep
    INNER JOIN public.ediciones ed ON ed.idedicion = ep.idedicion
    LEFT JOIN public.expositorevento ee ON ee.idevento = ep.idevento
    LEFT JOIN public.personal per ON per.idpersonal = ee.idpersonal
    GROUP BY ep.idevento, ep.idedicion, ep.nombreevento, ep.tipoevento,
             ep.fechahora, ep.aforo, ep.costoinscripcion,
             ed.anio, ed.nombreedicion;

CREATE OR REPLACE VIEW public.vw_Abonos AS
    SELECT
        ab.idabono       AS IdAbono,
        ab.idasistente   AS IdAsistente,
        ab.idtipoabono   AS IdTipoAbono,
        ab.idedicion     AS IdEdicion,
        ab.fechacompra   AS FechaCompra,
        ab.codigoacceso  AS CodigoAcceso,
        ab.pagado        AS Pagado,
        a.nombre         AS NombreAsistente,
        ta.nombreabono   AS NombreAbono,
        ta.precio        AS Precio,
        ta.descripcion   AS Descripcion,
        ed.anio          AS Anio,
        ed.nombreedicion AS NombreEdicion
    FROM public.abonos ab
    JOIN public.asistentes a   ON a.idasistente   = ab.idasistente
    JOIN public.tiposabono ta  ON ta.idtipoabono  = ab.idtipoabono
    JOIN public.ediciones ed   ON ed.idedicion    = ab.idedicion;

-- ============================================================
-- PASO 2: Procedimiento ComprarEntradaEvento
--         (estaba en _INIT_SQL de database.py)
-- ============================================================

CREATE OR REPLACE PROCEDURE public.ComprarEntradaEvento(
    p_IdAsistente   INT,
    p_IdEvento      INT,
    p_IdTarifa      INT,
    INOUT p_Resp    VARCHAR(300)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_aforo     INT;
    v_inscritos INT;
    v_nombre_ev VARCHAR(150);
BEGIN
    SELECT ep.aforo, ep.nombreevento
      INTO v_aforo, v_nombre_ev
      FROM public.eventosparalelos ep
     WHERE ep.idevento = p_IdEvento;

    IF NOT FOUND THEN
        p_Resp := 'Error: Evento paralelo no encontrado.'; RETURN;
    END IF;

    SELECT COUNT(*) INTO v_inscritos
      FROM public.entradas WHERE idevento = p_IdEvento;

    IF v_inscritos >= v_aforo THEN
        p_Resp := 'Error: Aforo agotado para "' || v_nombre_ev || '".'; RETURN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM public.tarifas WHERE idtarifa = p_IdTarifa) THEN
        p_Resp := 'Error: Tarifa no valida.'; RETURN;
    END IF;

    IF EXISTS (SELECT 1 FROM public.entradas WHERE idasistente = p_IdAsistente AND idevento = p_IdEvento) THEN
        p_Resp := 'Error: El asistente ya esta registrado en este evento.'; RETURN;
    END IF;

    INSERT INTO public.entradas (idasistente, idevento, idtarifa, fechacompra)
    VALUES (p_IdAsistente, p_IdEvento, p_IdTarifa, NOW());

    p_Resp := 'OK: Registro exitoso en "' || v_nombre_ev ||
              '". Lugar ' || (v_inscritos + 1) || ' de ' || v_aforo || '.';
EXCEPTION WHEN OTHERS THEN
    p_Resp := 'Error: ' || SQLERRM;
END; $$;

CREATE OR REPLACE FUNCTION public.fn_call_comprarentradaevento(
    p_IdAsistente INT, p_IdEvento INT, p_IdTarifa INT
) RETURNS TABLE (respuesta VARCHAR(300))
LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL public.ComprarEntradaEvento(p_IdAsistente, p_IdEvento, p_IdTarifa, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

-- ============================================================
-- PASO 3: Nuevas vistas para eliminar Raw SQL de views.py
-- ============================================================

-- Vista: Entradas con datos de asistente y pelicula
CREATE OR REPLACE VIEW public.vw_Entradas AS
    SELECT
        e.identrada    AS IdEntrada,
        e.idasistente  AS IdAsistente,
        e.idproyeccion AS IdProyeccion,
        e.idevento     AS IdEvento,
        e.idtarifa     AS IdTarifa,
        e.fechacompra  AS FechaCompra,
        a.nombre       AS Asistente,
        p.titulo       AS Pelicula,
        pr.fechahora   AS FechaHora
    FROM public.entradas e
    JOIN public.asistentes a ON a.idasistente = e.idasistente
    LEFT JOIN public.proyecciones pr ON pr.idproyeccion = e.idproyeccion
    LEFT JOIN public.peliculas p ON p.idpelicula = pr.idpelicula;

-- Vista: Personal completo
CREATE OR REPLACE VIEW public.vw_Personal AS
    SELECT
        idpersonal   AS IdPersonal,
        nombre       AS Nombre,
        biografia    AS Biografia,
        email        AS Email,
        telefono     AS Telefono,
        nacionalidad AS Nacionalidad
    FROM public.personal;

-- Vista: Evaluaciones con nombre de jurado, pelicula y categoria
CREATE OR REPLACE VIEW public.vw_Evaluaciones AS
    SELECT
        ev.idevaluacion    AS IdEvaluacion,
        ev.idmiembro       AS IdMiembro,
        ev.idpelicula      AS IdPelicula,
        ev.idcategoria     AS IdCategoria,
        ev.puntuacion      AS Puntuacion,
        ev.comentario      AS Comentario,
        m.nombre           AS Jurado,
        p.titulo           AS Pelicula,
        c.nombrecategoria  AS Categoria
    FROM public.evaluaciones ev
    JOIN public.miembrosjurado m ON m.idmiembro  = ev.idmiembro
    JOIN public.peliculas p      ON p.idpelicula = ev.idpelicula
    JOIN public.categorias c     ON c.idcategoria = ev.idcategoria;

-- Vista: Alojamientos con nombre de personal y hotel
CREATE OR REPLACE VIEW public.vw_Alojamientos AS
    SELECT
        a.idalojamiento  AS IdAlojamiento,
        a.idpersonal     AS IdPersonal,
        a.idhotel        AS IdHotel,
        a.idedicion      AS IdEdicion,
        a.nrohabitacion  AS NroHabitacion,
        a.checkin        AS CheckIn,
        a.checkout       AS CheckOut,
        p.nombre         AS Personal,
        h.nombrehotel    AS NombreHotel
    FROM public.alojamientos a
    JOIN public.personal p ON p.idpersonal = a.idpersonal
    JOIN public.hoteles h  ON h.idhotel   = a.idhotel;

-- Vista: Traslados con nombre de personal
CREATE OR REPLACE VIEW public.vw_Traslados AS
    SELECT
        t.idtraslado   AS IdTraslado,
        t.idpersonal   AS IdPersonal,
        t.idedicion    AS IdEdicion,
        t.tipotraslado AS TipoTraslado,
        t.origen       AS Origen,
        t.destino      AS Destino,
        t.fechahora    AS FechaHora,
        t.nrovuelo     AS NroVuelo,
        p.nombre       AS Personal
    FROM public.traslados t
    JOIN public.personal p ON p.idpersonal = t.idpersonal;

-- Vista: Patrocinios con nombre de empresa y edicion
CREATE OR REPLACE VIEW public.vw_Patrocinios AS
    SELECT
        pe.idpatrocinio    AS IdPatrocinio,
        pe.idpatrocinador  AS IdPatrocinador,
        pe.idedicion       AS IdEdicion,
        pe.tipoaporte      AS TipoAporte,
        pe.monto           AS Monto,
        pe.descripcionaporte AS DescripcionAporte,
        p.nombreempresa    AS NombreEmpresa,
        e.nombreedicion    AS NombreEdicion,
        e.anio             AS Anio
    FROM public.patrocinioedicion pe
    JOIN public.patrocinadores p ON p.idpatrocinador = pe.idpatrocinador
    JOIN public.ediciones e      ON e.idedicion      = pe.idedicion;

-- Vista: Competencia con titulo y categoria
CREATE OR REPLACE VIEW public.vw_Competencia AS
    SELECT
        cp.idpelicula   AS IdPelicula,
        cp.idcategoria  AS IdCategoria,
        cp.idedicion    AS IdEdicion,
        p.titulo        AS Titulo,
        c.nombrecategoria AS NombreCategoria
    FROM public.competenciapelicula cp
    JOIN public.peliculas p   ON p.idpelicula   = cp.idpelicula
    JOIN public.categorias c  ON c.idcategoria  = cp.idcategoria;

-- Vista: Roles de pelicula con nombre de personal y pelicula
CREATE OR REPLACE VIEW public.vw_RolesPelicula AS
    SELECT
        rp.idpersonal AS IdPersonal,
        rp.idpelicula AS IdPelicula,
        rp.rol        AS Rol,
        p.nombre      AS Personal,
        pe.titulo     AS Pelicula
    FROM public.rolespelicula rp
    JOIN public.personal p   ON p.idpersonal  = rp.idpersonal
    JOIN public.peliculas pe ON pe.idpelicula = rp.idpelicula;

-- Vista: Categorias por jurado (reemplaza el JOIN con filtro ?jurado=)
CREATE OR REPLACE VIEW public.vw_CategoriasPorJurado AS
    SELECT
        jc.idmiembro    AS IdMiembro,
        c.idcategoria   AS IdCategoria,
        c.nombrecategoria AS NombreCategoria
    FROM public.juradocategoria jc
    JOIN public.categorias c ON c.idcategoria = jc.idcategoria;

-- Vista: Peliculas por categoria (reemplaza el JOIN con filtro ?categoria=)
CREATE OR REPLACE VIEW public.vw_PeliculasPorCategoria AS
    SELECT
        cp.idcategoria  AS IdCategoria,
        p.idpelicula    AS IdPelicula,
        p.titulo        AS Titulo
    FROM public.competenciapelicula cp
    JOIN public.peliculas p ON p.idpelicula = cp.idpelicula;

-- ============================================================
-- PASO 4: Funciones para los Reportes (eliminan Raw SQL complejo)
-- ============================================================

-- Funcion: Reporte Financiero (reemplaza el UNION ALL de views.py)
CREATE OR REPLACE FUNCTION public.fn_reporte_financiero()
RETURNS TABLE (
    tipoventa  TEXT,
    categoria  TEXT,
    cantidad   INT,
    subtotal   FLOAT
)
LANGUAGE sql AS $$
    SELECT 'Entrada Individual'::TEXT      AS TipoVenta,
           t.nombretarifa::TEXT            AS Categoria,
           COUNT(e.identrada)::INT         AS Cantidad,
           COALESCE(SUM(t.precio), 0)::FLOAT AS Subtotal
      FROM public.entradas e
      INNER JOIN public.tarifas t ON t.idtarifa = e.idtarifa
     GROUP BY t.nombretarifa

    UNION ALL

    SELECT 'Abono'::TEXT                   AS TipoVenta,
           ta.nombreabono::TEXT            AS Categoria,
           COUNT(a.idabono)::INT           AS Cantidad,
           COALESCE(SUM(ta.precio), 0)::FLOAT AS Subtotal
      FROM public.abonos a
      INNER JOIN public.tiposabono ta ON ta.idtipoabono = a.idtipoabono
     WHERE a.pagado = TRUE
     GROUP BY ta.nombreabono

     ORDER BY TipoVenta, Subtotal DESC;
$$;

-- Funcion: Reporte Ocupacion por Sala
CREATE OR REPLACE FUNCTION public.fn_reporte_ocupacion()
RETURNS TABLE (
    nombresala          TEXT,
    nombresede          TEXT,
    capacidad           INT,
    entradasvendidas    INT,
    porcentajeocupacion FLOAT
)
LANGUAGE sql AS $$
    SELECT
        s.nombresala::TEXT                                                    AS NombreSala,
        se.nombresede::TEXT                                                   AS NombreSede,
        s.capacidad::INT                                                      AS Capacidad,
        COUNT(e.identrada)::INT                                               AS EntradasVendidas,
        ROUND(COUNT(e.identrada) * 100.0 / NULLIF(s.capacidad, 0), 2)::FLOAT AS PorcentajeOcupacion
    FROM public.salas s
    JOIN public.sedes se ON se.idsede = s.idsede
    LEFT JOIN public.proyecciones pr ON pr.idsala = s.idsala
    LEFT JOIN public.entradas e ON e.idproyeccion = pr.idproyeccion
    GROUP BY s.idsala, s.nombresala, se.nombresede, s.capacidad
    ORDER BY PorcentajeOcupacion DESC;
$$;

-- Funcion: Reporte Ranking de Peliculas
CREATE OR REPLACE FUNCTION public.fn_reporte_ranking()
RETURNS TABLE (
    titulo          TEXT,
    asistentes      INT,
    capacidadtotal  INT,
    pctocupacion    FLOAT
)
LANGUAGE sql AS $$
    SELECT
        p.titulo::TEXT                                                            AS Titulo,
        COUNT(e.identrada)::INT                                                   AS Asistentes,
        SUM(s.capacidad)::INT                                                     AS CapacidadTotal,
        ROUND(COUNT(e.identrada) * 100.0 / NULLIF(SUM(s.capacidad), 0), 2)::FLOAT AS PctOcupacion
    FROM public.peliculas p
    INNER JOIN public.proyecciones pr ON pr.idpelicula = p.idpelicula
    INNER JOIN public.salas s         ON s.idsala      = pr.idsala
    LEFT JOIN public.entradas e       ON e.idproyeccion = pr.idproyeccion
    GROUP BY p.titulo
    ORDER BY Asistentes DESC;
$$;

-- Funcion: Reporte Premiacion (devuelve tabla, reemplaza Raw SQL de views.py)
CREATE OR REPLACE FUNCTION public.fn_reporte_premiacion(
    p_id_edicion INT DEFAULT NULL
)
RETURNS TABLE (
    nombrecategoria  TEXT,
    peliculaganadora TEXT,
    promediojurado   FLOAT,
    anio             INT
)
LANGUAGE sql AS $$
    SELECT
        c.nombrecategoria::TEXT                       AS NombreCategoria,
        p.titulo::TEXT                                AS PeliculaGanadora,
        ROUND(AVG(ev.puntuacion), 2)::FLOAT           AS PromedioJurado,
        ed.anio::INT                                  AS Anio
    FROM public.premios pre
    INNER JOIN public.categorias c  ON c.idcategoria  = pre.idcategoria
    INNER JOIN public.peliculas p   ON p.idpelicula   = pre.idpelicula
    INNER JOIN public.ediciones ed  ON ed.idedicion   = pre.idedicion
    LEFT JOIN public.evaluaciones ev ON ev.idpelicula  = pre.idpelicula
                                    AND ev.idcategoria = pre.idcategoria
    WHERE (p_id_edicion IS NULL OR pre.idedicion = p_id_edicion)
    GROUP BY c.nombrecategoria, p.titulo, ed.anio
    ORDER BY c.nombrecategoria;
$$;

-- ============================================================
-- VERIFICACION FINAL
-- ============================================================
SELECT 'vw_Eventos'           AS Objeto, COUNT(*) AS Filas FROM public.vw_Eventos
UNION ALL
SELECT 'vw_Abonos',            COUNT(*) FROM public.vw_Abonos
UNION ALL
SELECT 'vw_Entradas',          COUNT(*) FROM public.vw_Entradas
UNION ALL
SELECT 'vw_Personal',          COUNT(*) FROM public.vw_Personal
UNION ALL
SELECT 'vw_Evaluaciones',      COUNT(*) FROM public.vw_Evaluaciones
UNION ALL
SELECT 'vw_Alojamientos',      COUNT(*) FROM public.vw_Alojamientos
UNION ALL
SELECT 'vw_Traslados',         COUNT(*) FROM public.vw_Traslados
UNION ALL
SELECT 'vw_Patrocinios',       COUNT(*) FROM public.vw_Patrocinios
UNION ALL
SELECT 'vw_Competencia',       COUNT(*) FROM public.vw_Competencia
UNION ALL
SELECT 'vw_RolesPelicula',     COUNT(*) FROM public.vw_RolesPelicula
UNION ALL
SELECT 'vw_CategoriasPorJurado', COUNT(*) FROM public.vw_CategoriasPorJurado
UNION ALL
SELECT 'vw_PeliculasPorCategoria', COUNT(*) FROM public.vw_PeliculasPorCategoria;
