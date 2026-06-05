-- ============================================================
-- FESTCINE — Script de corrección de vistas y funciones
-- Motor: PostgreSQL 18
-- ============================================================

-- 1. Vista de Eventos Paralelos con expositores
CREATE OR REPLACE VIEW vw_Eventos AS
SELECT
    ep.IdEvento,
    ep.IdEdicion,
    ep.NombreEvento,
    ep.TipoEvento,
    ep.FechaHora,
    ep.Aforo,
    ep.CostoInscripcion,
    e.NombreEdicion,
    e.Anio,
    STRING_AGG(per.Nombre, ', ' ORDER BY per.Nombre) AS Expositores
FROM EventosParalelos ep
JOIN Ediciones e ON e.IdEdicion = ep.IdEdicion
LEFT JOIN ExpositorEvento ee ON ee.IdEvento = ep.IdEvento
LEFT JOIN Personal per ON per.IdPersonal = ee.IdPersonal
GROUP BY ep.IdEvento, ep.IdEdicion, ep.NombreEvento, ep.TipoEvento,
         ep.FechaHora, ep.Aforo, ep.CostoInscripcion, e.NombreEdicion, e.Anio;

-- 2. Vista de Abonos (faltaba)
CREATE OR REPLACE VIEW vw_Abonos AS
SELECT
    ab.IdAbono,
    ab.IdAsistente,
    ab.IdTipoAbono,
    ab.IdEdicion,
    ab.FechaCompra,
    ab.CodigoAcceso,
    ab.Pagado,
    a.Nombre AS NombreAsistente,
    ta.NombreAbono,
    ta.Precio,
    e.NombreEdicion,
    e.Anio
FROM Abonos ab
JOIN Asistentes a ON a.IdAsistente = ab.IdAsistente
JOIN TiposAbono ta ON ta.IdTipoAbono = ab.IdTipoAbono
JOIN Ediciones e ON e.IdEdicion = ab.IdEdicion;

-- 3. Recrear vw_Peliculas con géneros concatenados
CREATE OR REPLACE VIEW vw_Peliculas AS
SELECT
    p.IdPelicula,
    p.Titulo,
    p.AnioProd,
    p.Duracion,
    p.PaisOrigen,
    p.Sinopsis,
    p.Clasificacion,
    p.Formato,
    p.Estado,
    STRING_AGG(g.NombreGenero, ', ' ORDER BY g.NombreGenero) AS Generos
FROM Peliculas p
LEFT JOIN PeliculaGenero pg ON pg.IdPelicula = p.IdPelicula
LEFT JOIN Generos g ON g.IdGenero = pg.IdGenero
GROUP BY p.IdPelicula, p.Titulo, p.AnioProd, p.Duracion, p.PaisOrigen,
         p.Sinopsis, p.Clasificacion, p.Formato, p.Estado;

-- 4. Recrear vw_Proyecciones con aforo dinámico
CREATE OR REPLACE VIEW vw_Proyecciones AS
SELECT
    pr.IdProyeccion,
    pr.IdPelicula,
    pr.IdSala,
    pr.IdEdicion,
    pr.FechaHora,
    pr.TieneQA,
    p.Titulo,
    s.NombreSala,
    s.Capacidad,
    se.NombreSede,
    e.NombreEdicion,
    e.Anio,
    (s.Capacidad - COUNT(en.IdEntrada)) AS AforoDisponible
FROM Proyecciones pr
JOIN Peliculas p ON p.IdPelicula = pr.IdPelicula
JOIN Salas s ON s.IdSala = pr.IdSala
JOIN Sedes se ON se.IdSede = s.IdSede
JOIN Ediciones e ON e.IdEdicion = pr.IdEdicion
LEFT JOIN Entradas en ON en.IdProyeccion = pr.IdProyeccion
GROUP BY pr.IdProyeccion, pr.IdPelicula, pr.IdSala, pr.IdEdicion,
         pr.FechaHora, pr.TieneQA, p.Titulo, s.NombreSala, s.Capacidad,
         se.NombreSede, e.NombreEdicion, e.Anio;

-- 5. Recrear vw_Asistentes
CREATE OR REPLACE VIEW vw_Asistentes AS
SELECT
    a.IdAsistente,
    a.Nombre,
    a.Email,
    a.Telefono,
    a.TipoAsistente,
    COUNT(DISTINCT en.IdEntrada) AS TotalEntradas,
    COUNT(DISTINCT ab.IdAbono) AS TotalAbonos
FROM Asistentes a
LEFT JOIN Entradas en ON en.IdAsistente = a.IdAsistente
LEFT JOIN Abonos ab ON ab.IdAsistente = a.IdAsistente
GROUP BY a.IdAsistente, a.Nombre, a.Email, a.Telefono, a.TipoAsistente;

-- 6. Recrear vw_Salas
CREATE OR REPLACE VIEW vw_Salas AS
SELECT
    s.IdSala,
    s.NombreSala,
    s.Capacidad,
    s.IdSede,
    se.NombreSede,
    se.Ciudad,
    se.Direccion
FROM Salas s
JOIN Sedes se ON se.IdSede = s.IdSede;

-- 7. Recrear vw_Tarifas
CREATE OR REPLACE VIEW vw_Tarifas AS
SELECT IdTarifa, NombreTarifa, Precio, TipoAsistente
FROM Tarifas
ORDER BY Precio;

-- 8. Recrear vw_TiposAbono
CREATE OR REPLACE VIEW vw_TiposAbono AS
SELECT IdTipoAbono, NombreAbono, Precio, TipoAcceso, DuracionDias
FROM TiposAbono
ORDER BY Precio;

-- ============================================================
-- FUNCIONES WRAPPER
-- ============================================================

-- 9. Wrapper para ProgramarProyeccion
CREATE OR REPLACE FUNCTION fn_call_programarproyeccion(
    p_IdPelicula INT, p_IdSala INT, p_IdEdicion INT,
    p_FechaHora TIMESTAMP, p_TieneQA BOOLEAN
) RETURNS TABLE (respuesta VARCHAR(300))
LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL ProgramarProyeccion(p_IdPelicula, p_IdSala, p_IdEdicion, p_FechaHora, p_TieneQA, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

-- 10. Wrapper para ComprarEntrada
CREATE OR REPLACE FUNCTION fn_call_comprarentrada(
    p_IdAsistente INT, p_IdProyeccion INT, p_IdTarifa INT
) RETURNS TABLE (respuesta VARCHAR(300))
LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL ComprarEntrada(p_IdAsistente, p_IdProyeccion, p_IdTarifa, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

-- 11. Wrapper para VenderAbono
CREATE OR REPLACE FUNCTION fn_call_venderabono(
    p_IdAsistente INT, p_IdTipoAbono INT, p_IdEdicion INT, p_PagoExitoso BOOLEAN
) RETURNS TABLE (respuesta VARCHAR(300))
LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL VenderAbono(p_IdAsistente, p_IdTipoAbono, p_IdEdicion, p_PagoExitoso, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

-- ============================================================
-- PROCEDIMIENTO ComprarEntradaEvento (nuevo — sin CodigoEntrada)
-- ============================================================
CREATE OR REPLACE PROCEDURE ComprarEntradaEvento(
    p_IdAsistente   INT,
    p_IdEvento      INT,
    p_IdTarifa      INT,
    INOUT p_Resp    VARCHAR(300)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_aforo        INT;
    v_inscritos    INT;
    v_nombre_ev    VARCHAR(120);
    v_tipo_asi     VARCHAR(30);
    v_costo        NUMERIC(10,2);
BEGIN
    -- Verificar que el evento existe
    SELECT ep.Aforo, ep.NombreEvento, ep.CostoInscripcion
      INTO v_aforo, v_nombre_ev, v_costo
      FROM EventosParalelos ep
     WHERE ep.IdEvento = p_IdEvento;

    IF NOT FOUND THEN
        p_Resp := 'Error: Evento paralelo no encontrado.';
        RETURN;
    END IF;

    -- Contar inscritos actuales
    SELECT COUNT(*) INTO v_inscritos
      FROM Entradas
     WHERE IdEvento = p_IdEvento;

    IF v_inscritos >= v_aforo THEN
        p_Resp := 'Error: Aforo agotado para el evento "' || v_nombre_ev || '".';
        RETURN;
    END IF;

    -- Verificar que la tarifa existe
    IF NOT EXISTS (SELECT 1 FROM Tarifas WHERE IdTarifa = p_IdTarifa) THEN
        p_Resp := 'Error: Tarifa no válida.';
        RETURN;
    END IF;

    -- Verificar que el asistente no está ya registrado en este evento
    IF EXISTS (
        SELECT 1 FROM Entradas
         WHERE IdAsistente = p_IdAsistente AND IdEvento = p_IdEvento
    ) THEN
        p_Resp := 'Error: El asistente ya está registrado en este evento.';
        RETURN;
    END IF;

    -- Registrar la entrada al evento
    INSERT INTO Entradas (IdAsistente, IdEvento, IdTarifa, FechaCompra)
    VALUES (p_IdAsistente, p_IdEvento, p_IdTarifa, NOW());

    p_Resp := 'OK: Entrada registrada exitosamente para el evento "' || v_nombre_ev || 
              '". Lugar: ' || (v_inscritos + 1) || ' / ' || v_aforo || '.';

EXCEPTION WHEN OTHERS THEN
    p_Resp := 'Error: ' || SQLERRM;
END;
$$;

-- 12. Wrapper para ComprarEntradaEvento
CREATE OR REPLACE FUNCTION fn_call_comprarentradaevento(
    p_IdAsistente INT, p_IdEvento INT, p_IdTarifa INT
) RETURNS TABLE (respuesta VARCHAR(300))
LANGUAGE plpgsql AS $$
DECLARE v_resp VARCHAR(300);
BEGIN
    CALL ComprarEntradaEvento(p_IdAsistente, p_IdEvento, p_IdTarifa, v_resp);
    RETURN QUERY SELECT v_resp;
END; $$;

-- ============================================================
SELECT 'OK: Todas las vistas y funciones han sido creadas/actualizadas.' AS resultado;
