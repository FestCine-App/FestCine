import os
import re
import pg8000.native
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "festcine"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

_COLUMN_CASE = {
    "aforo": "Aforo", "aforodisponible": "AforoDisponible", "anio": "Anio",
    "anioprod": "AnioProd", "biografia": "Biografia", "capacidad": "Capacidad",
    "checkin": "CheckIn", "checkout": "CheckOut", "ciudad": "Ciudad",
    "clasificacion": "Clasificacion", "codigoacceso": "CodigoAcceso",
    "comentario": "Comentario", "contacto": "Contacto", "costoinscripcion": "CostoInscripcion",
    "descripcion": "Descripcion", "descripcionaporte": "DescripcionAporte",
    "destino": "Destino", "direccion": "Direccion", "duracion": "Duracion",
    "email": "Email", "estado": "Estado", "estrellas": "Estrellas",
    "expositores": "Expositores", "fechacompra": "FechaCompra", "fechafin": "FechaFin",
    "fechahora": "FechaHora", "fechainicio": "FechaInicio", "formato": "Formato",
    "generos": "Generos", "idabono": "IdAbono", "idalojamiento": "IdAlojamiento",
    "idasistente": "IdAsistente", "idcategoria": "IdCategoria", "idedicion": "IdEdicion",
    "identrada": "IdEntrada", "idevaluacion": "IdEvaluacion", "idevento": "IdEvento",
    "idgenero": "IdGenero", "idhotel": "IdHotel", "idmiembro": "IdMiembro",
    "idpatrocinador": "IdPatrocinador", "idpatrocinio": "IdPatrocinio",
    "idpelicula": "IdPelicula", "idpersonal": "IdPersonal", "idpremio": "IdPremio",
    "idproyeccion": "IdProyeccion", "idsala": "IdSala", "idsede": "IdSede",
    "idtarifa": "IdTarifa", "idtipoabono": "IdTipoAbono", "idtraslado": "IdTraslado",
    "monto": "Monto", "nacionalidad": "Nacionalidad", "nombre": "Nombre",
    "nombreabono": "NombreAbono", "nombrecategoria": "NombreCategoria",
    "nombreedicion": "NombreEdicion", "nombreempresa": "NombreEmpresa",
    "nombreevento": "NombreEvento", "nombregenero": "NombreGenero",
    "nombrehotel": "NombreHotel", "nombresala": "NombreSala", "nombresede": "NombreSede",
    "nombretarifa": "NombreTarifa", "nrohabitacion": "NroHabitacion",
    "nrovuelo": "NroVuelo", "origen": "Origen", "pagado": "Pagado",
    "pais": "Pais", "paisorigen": "PaisOrigen", "precio": "Precio",
    "profesion": "Profesion", "puntuacion": "Puntuacion", "redessociales": "RedesSociales",
    "respuesta": "Respuesta", "rol": "Rol", "sinopsis": "Sinopsis", "sitioweb": "SitioWeb",
    "telefono": "Telefono", "tieneqa": "TieneQA", "tipoaporte": "TipoAporte",
    "tipoasistente": "TipoAsistente", "tipoevento": "TipoEvento",
    "tipotraslado": "TipoTraslado", "titulo": "Titulo",
    "asistentes": "Asistentes", "capacidadtotal": "CapacidadTotal", "cantidad": "Cantidad",
    "nombreasistente": "NombreAsistente", "titulopelicula": "TituloPelicula",
    "total": "Total", "entradasvendidas": "EntradasVendidas", "porcentajeocupacion": "PorcentajeOcupacion",
    "pctocupacion": "PctOcupacion", "peliculaganadora": "PeliculaGanadora",
    "promediojurado": "PromedioJurado", "subtotal": "Subtotal",
    "asistente": "Asistente", "pelicula": "Pelicula", "resultado": "Resultado",
}

def _to_pascal(key):
    return _COLUMN_CASE.get(key, key[0].upper() + key[1:] if key else key)

def _convert(sql, params):
    if not params:
        return sql, {}
    parts = re.split(r'%s', sql)
    new_sql = ''.join(
        part + f'${i+1}' if i < len(parts) - 1 else part
        for i, part in enumerate(parts)
    )
    return new_sql, {str(i): v for i, v in enumerate(params, 1)}

def _to_dicts(rows, conn):
    if not rows or not conn.columns:
        return rows if rows else []
    cols = [_to_pascal(c["name"]) for c in conn.columns]
    return [dict(zip(cols, row)) for row in rows]

def _to_dict(row, conn):
    if not row or not conn.columns:
        return row
    cols = [_to_pascal(c["name"]) for c in conn.columns]
    return dict(zip(cols, row))

def query(sql, params=None):
    conn = pg8000.native.Connection(**DB_CONFIG)
    try:
        sql, params_dict = _convert(sql, params)
        if params_dict:
            rows = conn.run(sql, **params_dict)
        else:
            rows = conn.run(sql)
        return _to_dicts(rows, conn)
    finally:
        try:
            conn.close()
        except Exception:
            pass

def query_one(sql, params=None):
    conn = pg8000.native.Connection(**DB_CONFIG)
    try:
        sql, params_dict = _convert(sql, params)
        if params_dict:
            rows = conn.run(sql, **params_dict)
        else:
            rows = conn.run(sql)
        if not rows:
            return None
        return _to_dict(rows[0], conn)
    finally:
        try:
            conn.close()
        except Exception:
            pass

def call_procedure(sql, params=None):
    return query(sql, params)


# ============================================================
# AUTO-INICIALIZACIÓN: Crea vistas y funciones faltantes al
# arrancar el servidor Django.
# Solo crea/actualiza lo que realmente falta en la BD.
# ============================================================
_INIT_SQL = [

    # --- Vista: Eventos Paralelos (NUEVA - no existe en BD) ---
    # EventosParalelos no tiene IdEdicion, es autónoma.
    """
    CREATE OR REPLACE VIEW vw_Eventos AS
    SELECT
        ep.idevento   AS IdEvento,
        ep.nombreevento AS NombreEvento,
        ep.tipoevento AS TipoEvento,
        ep.fechahora  AS FechaHora,
        ep.aforo      AS Aforo,
        ep.costoinscripcion AS CostoInscripcion,
        STRING_AGG(per.nombre, ', ' ORDER BY per.nombre) AS Expositores
    FROM eventosparalelos ep
    LEFT JOIN expositorevento ee ON ee.idevento = ep.idevento
    LEFT JOIN personal per ON per.idpersonal = ee.idpersonal
    GROUP BY ep.idevento, ep.nombreevento, ep.tipoevento,
             ep.fechahora, ep.aforo, ep.costoinscripcion
    """,

    # --- Vista: Abonos (NUEVA - no existe en BD) ---
    # Abonos no tiene IdEdicion según la estructura real.
    """
    CREATE OR REPLACE VIEW vw_Abonos AS
    SELECT
        ab.idabono      AS IdAbono,
        ab.idasistente  AS IdAsistente,
        ab.idtipoabono  AS IdTipoAbono,
        ab.fechacompra  AS FechaCompra,
        ab.codigoacceso AS CodigoAcceso,
        ab.pagado       AS Pagado,
        a.nombre        AS NombreAsistente,
        ta.nombreabono  AS NombreAbono,
        ta.precio       AS Precio,
        ta.descripcion  AS Descripcion
    FROM abonos ab
    JOIN asistentes a  ON a.idasistente  = ab.idasistente
    JOIN tiposabono ta ON ta.idtipoabono = ab.idtipoabono
    """,

    # --- Procedimiento: ComprarEntradaEvento (NUEVO - no existe en BD) ---
    """
    CREATE OR REPLACE PROCEDURE ComprarEntradaEvento(
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
          FROM eventosparalelos ep
         WHERE ep.idevento = p_IdEvento;

        IF NOT FOUND THEN
            p_Resp := 'Error: Evento paralelo no encontrado.'; RETURN;
        END IF;

        SELECT COUNT(*) INTO v_inscritos
          FROM entradas WHERE idevento = p_IdEvento;

        IF v_inscritos >= v_aforo THEN
            p_Resp := 'Error: Aforo agotado para "' || v_nombre_ev || '".'; RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM tarifas WHERE idtarifa = p_IdTarifa) THEN
            p_Resp := 'Error: Tarifa no valida.'; RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM entradas WHERE idasistente = p_IdAsistente AND idevento = p_IdEvento) THEN
            p_Resp := 'Error: El asistente ya esta registrado en este evento.'; RETURN;
        END IF;

        INSERT INTO entradas (idasistente, idevento, idtarifa, fechacompra)
        VALUES (p_IdAsistente, p_IdEvento, p_IdTarifa, NOW());

        p_Resp := 'OK: Registro exitoso en "' || v_nombre_ev ||
                  '". Lugar ' || (v_inscritos + 1) || ' de ' || v_aforo || '.';
    EXCEPTION WHEN OTHERS THEN
        p_Resp := 'Error: ' || SQLERRM;
    END; $$
    """,

    # --- Función wrapper: fn_call_comprarentradaevento ---
    """
    CREATE OR REPLACE FUNCTION fn_call_comprarentradaevento(
        p_IdAsistente INT, p_IdEvento INT, p_IdTarifa INT
    ) RETURNS TABLE (respuesta VARCHAR(300))
    LANGUAGE plpgsql AS $$
    DECLARE v_resp VARCHAR(300);
    BEGIN
        CALL ComprarEntradaEvento(p_IdAsistente, p_IdEvento, p_IdTarifa, v_resp);
        RETURN QUERY SELECT v_resp;
    END; $$
    """,

    # --- Función wrapper: fn_call_comprarentrada ---
    """
    CREATE OR REPLACE FUNCTION fn_call_comprarentrada(
        p_IdAsistente INT, p_IdProyeccion INT, p_IdTarifa INT
    ) RETURNS TABLE (respuesta VARCHAR(300))
    LANGUAGE plpgsql AS $$
    DECLARE v_resp VARCHAR(300);
    BEGIN
        CALL ComprarEntrada(p_IdAsistente, p_IdProyeccion, p_IdTarifa, v_resp);
        RETURN QUERY SELECT v_resp;
    END; $$
    """,

    # --- Función wrapper: fn_call_programarproyeccion ---
    # ProgramarProyeccion real: (p_IdPelicula, p_IdSala, p_FechaHora, p_TieneQA, OUT p_IdNuevo, OUT p_Respuesta)
    """
    CREATE OR REPLACE FUNCTION fn_call_programarproyeccion(
        p_IdPelicula INT, p_IdSala INT,
        p_FechaHora TIMESTAMP, p_TieneQA BOOLEAN
    ) RETURNS TABLE (respuesta VARCHAR)
    LANGUAGE plpgsql AS $$
    DECLARE
        v_id   INT;
        v_resp VARCHAR;
    BEGIN
        CALL ProgramarProyeccion(p_IdPelicula, p_IdSala, p_FechaHora, p_TieneQA, v_id, v_resp);
        RETURN QUERY SELECT v_resp;
    END; $$
    """,

    # --- Función wrapper: fn_call_venderabono ---
    # VenderAbono real: (p_IdAsistente, p_IdTipoAbono, p_PagoExitoso, OUT p_Respuesta)
    """
    CREATE OR REPLACE FUNCTION fn_call_venderabono(
        p_IdAsistente INT, p_IdTipoAbono INT, p_PagoExitoso BOOLEAN
    ) RETURNS TABLE (respuesta VARCHAR)
    LANGUAGE plpgsql AS $$
    DECLARE v_resp VARCHAR;
    BEGIN
        CALL VenderAbono(p_IdAsistente, p_IdTipoAbono, p_PagoExitoso, v_resp);
        RETURN QUERY SELECT v_resp;
    END; $$
    """,
]

def _auto_init():
    """Ejecuta todas las sentencias DDL de inicialización al arrancar."""
    try:
        conn = pg8000.native.Connection(**DB_CONFIG)
        # Intentar activar autocommit; si no es soportado, usar commit() manual
        try:
            conn.autocommit = True
            use_autocommit = True
        except Exception:
            use_autocommit = False

        for stmt in _INIT_SQL:
            try:
                conn.run(stmt.strip())
                if not use_autocommit:
                    conn.run("COMMIT")
            except Exception as e:
                # Si hay un error, hacer rollback y continuar con el siguiente
                try:
                    conn.run("ROLLBACK")
                except Exception:
                    pass
                print(f"[festcine db-init] Advertencia: {e}")
        conn.close()
        print("[festcine db-init] Vistas y funciones verificadas/creadas correctamente.")
    except Exception as e:
        print(f"[festcine db-init] Error durante inicialización: {e}")

_auto_init()
