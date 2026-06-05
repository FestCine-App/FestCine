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
    "nombretarifa": "NombreTarifa", "asistente": "Asistente", "pelicula": "Pelicula",
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
