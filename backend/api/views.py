import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from config.database import query, query_one, call_vender_abono

def _json(data, status=200):
    return JsonResponse(data, safe=False, status=status)

def _body(request):
    return json.loads(request.body) if request.body else {}

def _not_found(msg="No encontrado"):
    return _json({"error": msg}, 404)

def _error(msg, status=400):
    return _json({"error": msg}, status)

def _db_error(e):
    """Convierte una excepción de BD en respuesta JSON amigable (nunca HTML)."""
    msg = str(e)
    if "unique" in msg.lower() or "duplicate" in msg.lower():
        return _json({"error": "Ya existe un registro igual (restricción de unicidad). Verifique los datos."}, 409)
    if "foreign key" in msg.lower() or "violates" in msg.lower():
        return _json({"error": "Error de integridad: referencia inválida en la base de datos."}, 400)
    if "not null" in msg.lower():
        return _json({"error": "Faltan datos obligatorios."}, 400)
    return _json({"error": f"Error de base de datos: {msg}"}, 500)

def _current_edicion_id():
    """Devuelve el IdEdicion de la edición vigente (la de año más reciente)."""
    r = query_one('SELECT IdEdicion FROM Ediciones ORDER BY Anio DESC LIMIT 1')
    return r["IdEdicion"] if r else None

# --- PELICULAS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def peliculas(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Peliculas WHERE IdPelicula=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Peliculas')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO Peliculas (Titulo,AnioProd,Duracion,PaisOrigen,Sinopsis,Clasificacion,Formato,Estado) '
            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING IdPelicula',
            (data["Titulo"], data["AnioProd"], data["Duracion"], data["PaisOrigen"],
             data.get("Sinopsis"), data["Clasificacion"], data["Formato"], data.get("Estado", "Postulada")))
        pid = r["IdPelicula"]
        for g in data.get("generos", []):
            query('INSERT INTO PeliculaGenero (IdPelicula,IdGenero) VALUES (%s,%s)', (pid, g))
        return _json({"id": pid}, 201)

    if request.method == "PUT":
        data = _body(request)
        query(
            'UPDATE Peliculas SET Titulo=%s,AnioProd=%s,Duracion=%s,PaisOrigen=%s,'
            'Sinopsis=%s,Clasificacion=%s,Formato=%s,Estado=%s WHERE IdPelicula=%s',
            (data["Titulo"], data["AnioProd"], data["Duracion"], data["PaisOrigen"],
             data.get("Sinopsis"), data["Clasificacion"], data["Formato"], data["Estado"], id))
        if "generos" in data:
            query('DELETE FROM PeliculaGenero WHERE IdPelicula=%s', (id,))
            for g in data["generos"]:
                query('INSERT INTO PeliculaGenero (IdPelicula,IdGenero) VALUES (%s,%s)', (id, g))
        return _json({"message": "Actualizada"})

    if request.method == "DELETE":
        query('DELETE FROM PeliculaGenero WHERE IdPelicula=%s', (id,))
        query('DELETE FROM Peliculas WHERE IdPelicula=%s', (id,))
        return _json({"message": "Eliminada"})

# --- PROYECCIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def proyecciones(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Proyecciones WHERE IdProyeccion=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Proyecciones ORDER BY FechaHora')])

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            rows = query(
                'SELECT * FROM fn_call_programarproyeccion(%s,%s,%s,%s,%s)',
                (data["IdPelicula"], data["IdSala"], id_edicion, data["FechaHora"], data.get("TieneQA", False)))
            msg = rows[0]["Respuesta"] if rows else ""
            if msg.startswith("Error"):
                return _error(msg, 409)
            return _json({"message": msg}, 201)
        except Exception as e:
            return _error(str(e).split("\n")[0], 409)

    if request.method == "DELETE":
        query('DELETE FROM Entradas WHERE IdProyeccion=%s', (id,))
        query('DELETE FROM Proyecciones WHERE IdProyeccion=%s', (id,))
        return _json({"message": "Eliminada"})

# --- ASISTENTES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def asistentes(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Asistentes WHERE IdAsistente=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Asistentes ORDER BY Nombre')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO Asistentes (Nombre, Email, Telefono, TipoAsistente) VALUES (%s,%s,%s,%s) RETURNING IdAsistente',
            (data["Nombre"], data["Email"], data.get("Telefono"), data.get("TipoAsistente", "General")))
        return _json({"id": r["IdAsistente"]}, 201)

# --- ENTRADAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def entradas(request):
    if request.method == "GET":
        return _json([dict(r) for r in query('SELECT * FROM vw_Entradas ORDER BY FechaCompra DESC')])

    if request.method == "POST":
        data = _body(request)
        try:
            if data.get("IdProyeccion"):
                rows = query(
                    'SELECT * FROM fn_call_comprarentrada(%s,%s,%s)',
                    (int(data["IdAsistente"]), int(data["IdProyeccion"]), int(data["IdTarifa"])))
            elif data.get("IdEvento"):
                rows = query(
                    'SELECT * FROM fn_call_comprarentradaevento(%s,%s,%s)',
                    (int(data["IdAsistente"]), int(data["IdEvento"]), int(data["IdTarifa"])))
            else:
                return _error("Debe especificar una proyeccion o un evento")

            msg = rows[0]["Respuesta"] if rows else ""
            if msg.startswith("Error"):
                return _error(msg)
            return _json({"message": msg}, 201)
        except Exception as e:
            return _error(str(e).split("\n")[0])

# --- ABONOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def abonos(request):
    if request.method == "GET":
        return _json([dict(r) for r in query('SELECT * FROM vw_Abonos ORDER BY FechaCompra DESC')])

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            msg = call_vender_abono(
                int(data["IdAsistente"]),
                int(data["IdTipoAbono"]),
                int(id_edicion),
                bool(data.get("PagoExitoso", True))
            )
            if msg.startswith("Error"):
                return _error(msg)
            return _json({"message": msg}, 201)
        except Exception as e:
            return _error(str(e).split("\n")[0])

# --- SEDES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def sedes(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Sedes WHERE IdSede=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM Sedes ORDER BY NombreSede')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO Sedes (NombreSede, Direccion, Ciudad, SitioWeb) VALUES (%s,%s,%s,%s) RETURNING IdSede',
            (data["NombreSede"], data.get("Direccion"), data.get("Ciudad"), data.get("SitioWeb")))
        return _json({"id": r["IdSede"]}, 201)

    if request.method == "DELETE":
        query('DELETE FROM Salas WHERE IdSede=%s', (id,))
        query('DELETE FROM Sedes WHERE IdSede=%s', (id,))
        return _json({"message": "Eliminada"})

# --- SALAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def salas(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Salas WHERE IdSala=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Salas ORDER BY NombreSede, NombreSala')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO Salas (NombreSala, Capacidad, IdSede) VALUES (%s,%s,%s) RETURNING IdSala',
            (data["NombreSala"], data["Capacidad"], data["IdSede"]))
        return _json({"id": r["IdSala"]}, 201)

# --- EVENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def eventos(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Eventos WHERE IdEvento=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Eventos ORDER BY FechaHora')])

    if request.method == "POST":
        try:
            data = _body(request)
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            r = query_one(
                'INSERT INTO EventosParalelos (IdEdicion, NombreEvento, TipoEvento, FechaHora, Aforo, CostoInscripcion) '
                'VALUES (%s,%s,%s,%s,%s,%s) RETURNING IdEvento',
                (id_edicion, data["NombreEvento"], data["TipoEvento"], data["FechaHora"],
                 data["Aforo"], data.get("CostoInscripcion", 0)))
            eid = r["IdEvento"]
            for p in data.get("expositores", []):
                query('INSERT INTO ExpositorEvento (IdEvento, IdPersonal) VALUES (%s,%s)', (eid, p))
            return _json({"id": eid}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        query(
            'UPDATE EventosParalelos SET NombreEvento=%s, TipoEvento=%s, FechaHora=%s, '
            'Aforo=%s, CostoInscripcion=%s WHERE IdEvento=%s',
            (data["NombreEvento"], data["TipoEvento"], data["FechaHora"],
             data["Aforo"], data.get("CostoInscripcion", 0), id))
        if "expositores" in data:
            query('DELETE FROM ExpositorEvento WHERE IdEvento=%s', (id,))
            for p in data["expositores"]:
                query('INSERT INTO ExpositorEvento (IdEvento, IdPersonal) VALUES (%s,%s)', (id, p))
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        query('DELETE FROM Entradas WHERE IdEvento=%s', (id,))
        query('DELETE FROM ExpositorEvento WHERE IdEvento=%s', (id,))
        query('DELETE FROM EventosParalelos WHERE IdEvento=%s', (id,))
        return _json({"message": "Eliminado"})

# --- GENEROS ---
@csrf_exempt
@require_http_methods(["GET"])
def generos(request):
    return _json([dict(r) for r in query('SELECT * FROM Generos ORDER BY NombreGenero')])

# --- PERSONAL ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def personal(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Personal WHERE IdPersonal=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Personal ORDER BY Nombre')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO Personal (Nombre, Biografia, Email, Telefono, Nacionalidad) VALUES (%s,%s,%s,%s,%s) RETURNING IdPersonal',
            (data["Nombre"], data.get("Biografia"), data.get("Email"), data.get("Telefono"), data.get("Nacionalidad")))
        return _json({"id": r["IdPersonal"]}, 201)

    if request.method == "PUT":
        data = _body(request)
        query(
            'UPDATE Personal SET Nombre=%s, Biografia=%s, Email=%s, Telefono=%s, Nacionalidad=%s WHERE IdPersonal=%s',
            (data["Nombre"], data.get("Biografia"), data.get("Email"), data.get("Telefono"), data.get("Nacionalidad"), id))
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        query('DELETE FROM RolesPelicula WHERE IdPersonal=%s', (id,))
        query('DELETE FROM ExpositorEvento WHERE IdPersonal=%s', (id,))
        query('DELETE FROM Alojamientos WHERE IdPersonal=%s', (id,))
        query('DELETE FROM Traslados WHERE IdPersonal=%s', (id,))
        query('DELETE FROM Personal WHERE IdPersonal=%s', (id,))
        return _json({"message": "Eliminado"})

# --- CATEGORIAS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def categorias(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Categorias WHERE IdCategoria=%s', (id,))
            return _json(r) if r else _not_found()
        jurado_id   = request.GET.get('jurado')
        categoria_id = request.GET.get('categoria')
        if jurado_id:
            return _json([dict(r) for r in query(
                'SELECT * FROM vw_CategoriasPorJurado WHERE IdMiembro=%s ORDER BY NombreCategoria',
                [jurado_id])])
        if categoria_id:
            return _json([dict(r) for r in query(
                'SELECT * FROM vw_PeliculasPorCategoria WHERE IdCategoria=%s ORDER BY Titulo',
                [categoria_id])])
        return _json([dict(r) for r in query('SELECT * FROM Categorias ORDER BY NombreCategoria')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO Categorias (NombreCategoria, Descripcion) VALUES (%s,%s) RETURNING IdCategoria',
            (data["NombreCategoria"], data.get("Descripcion")))
        return _json({"id": r["IdCategoria"]}, 201)

    if request.method == "PUT":
        data = _body(request)
        query('UPDATE Categorias SET NombreCategoria=%s, Descripcion=%s WHERE IdCategoria=%s',
              (data["NombreCategoria"], data.get("Descripcion"), id))
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        query('DELETE FROM CompetenciaPelicula WHERE IdCategoria=%s', (id,))
        query('DELETE FROM JuradoCategoria WHERE IdCategoria=%s', (id,))
        query('DELETE FROM Evaluaciones WHERE IdCategoria=%s', (id,))
        query('DELETE FROM Premios WHERE IdCategoria=%s', (id,))
        query('DELETE FROM Categorias WHERE IdCategoria=%s', (id,))
        return _json({"message": "Eliminado"})

# --- JURADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def jurados(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM MiembrosJurado WHERE IdMiembro=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM MiembrosJurado ORDER BY Nombre')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO MiembrosJurado (Nombre, Profesion, Pais, Email) VALUES (%s,%s,%s,%s) RETURNING IdMiembro',
            (data["Nombre"], data.get("Profesion"), data.get("Pais"), data.get("Email")))
        return _json({"id": r["IdMiembro"]}, 201)

    if request.method == "PUT":
        data = _body(request)
        query('UPDATE MiembrosJurado SET Nombre=%s, Profesion=%s, Pais=%s, Email=%s WHERE IdMiembro=%s',
              (data["Nombre"], data.get("Profesion"), data.get("Pais"), data.get("Email"), id))
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        query('DELETE FROM JuradoCategoria WHERE IdMiembro=%s', (id,))
        query('DELETE FROM Evaluaciones WHERE IdMiembro=%s', (id,))
        query('DELETE FROM MiembrosJurado WHERE IdMiembro=%s', (id,))
        return _json({"message": "Eliminado"})

# --- EVALUACIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def evaluaciones(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Evaluaciones WHERE IdEvaluacion=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Evaluaciones ORDER BY IdEvaluacion')])

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            r = query_one(
                'INSERT INTO Evaluaciones (IdMiembro, IdPelicula, IdCategoria, IdEdicion, Puntuacion, Comentario) '
                'VALUES (%s,%s,%s,%s,%s,%s) RETURNING IdEvaluacion',
                (data["IdMiembro"], data["IdPelicula"], data["IdCategoria"],
                 id_edicion, data["Puntuacion"], data.get("Comentario")))
            return _json({"id": r["IdEvaluacion"]}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            query(
                'UPDATE Evaluaciones SET IdMiembro=%s, IdPelicula=%s, IdCategoria=%s, '
                'IdEdicion=%s, Puntuacion=%s, Comentario=%s WHERE IdEvaluacion=%s',
                (data["IdMiembro"], data["IdPelicula"], data["IdCategoria"],
                 id_edicion, data["Puntuacion"], data.get("Comentario"), id))
            return _json({"message": "Actualizado"})
        except Exception as e:
            return _db_error(e)

    if request.method == "DELETE":
        query('DELETE FROM Evaluaciones WHERE IdEvaluacion=%s', (id,))
        return _json({"message": "Eliminado"})

# --- PATROCINADORES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def patrocinadores(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Patrocinadores WHERE IdPatrocinador=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM Patrocinadores ORDER BY NombreEmpresa')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO Patrocinadores (NombreEmpresa, Contacto, Email, RedesSociales) VALUES (%s,%s,%s,%s) RETURNING IdPatrocinador',
            (data["NombreEmpresa"], data.get("Contacto"), data.get("Email"), data.get("RedesSociales")))
        return _json({"id": r["IdPatrocinador"]}, 201)

    if request.method == "PUT":
        data = _body(request)
        query(
            'UPDATE Patrocinadores SET NombreEmpresa=%s, Contacto=%s, Email=%s, RedesSociales=%s WHERE IdPatrocinador=%s',
            (data["NombreEmpresa"], data.get("Contacto"), data.get("Email"), data.get("RedesSociales"), id))
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        query('DELETE FROM PatrocinioEdicion WHERE IdPatrocinador=%s', (id,))
        query('DELETE FROM Patrocinadores WHERE IdPatrocinador=%s', (id,))
        return _json({"message": "Eliminado"})

# --- PATROCINIOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def patrocinios(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Patrocinios WHERE IdPatrocinio=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Patrocinios ORDER BY Anio DESC')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO PatrocinioEdicion (IdPatrocinador, IdEdicion, TipoAporte, Monto, DescripcionAporte) '
            'VALUES (%s,%s,%s,%s,%s) RETURNING IdPatrocinio',
            (data["IdPatrocinador"], data["IdEdicion"], data["TipoAporte"],
             data.get("Monto"), data.get("DescripcionAporte")))
        return _json({"id": r["IdPatrocinio"]}, 201)

    if request.method == "PUT":
        data = _body(request)
        query(
            'UPDATE PatrocinioEdicion SET IdPatrocinador=%s, IdEdicion=%s, TipoAporte=%s, '
            'Monto=%s, DescripcionAporte=%s WHERE IdPatrocinio=%s',
            (data["IdPatrocinador"], data["IdEdicion"], data["TipoAporte"],
             data.get("Monto"), data.get("DescripcionAporte"), id))
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        query('DELETE FROM PatrocinioEdicion WHERE IdPatrocinio=%s', (id,))
        return _json({"message": "Eliminado"})

# --- EDICIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def ediciones(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Ediciones WHERE IdEdicion=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM Ediciones ORDER BY Anio DESC')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO Ediciones (Anio, NombreEdicion, FechaInicio, FechaFin) VALUES (%s,%s,%s,%s) RETURNING IdEdicion',
            (data["Anio"], data["NombreEdicion"], data["FechaInicio"], data["FechaFin"]))
        return _json({"id": r["IdEdicion"]}, 201)

    if request.method == "PUT":
        data = _body(request)
        query(
            'UPDATE Ediciones SET Anio=%s, NombreEdicion=%s, FechaInicio=%s, FechaFin=%s WHERE IdEdicion=%s',
            (data["Anio"], data["NombreEdicion"], data["FechaInicio"], data["FechaFin"], id))
        return _json({"message": "Actualizada"})

    if request.method == "DELETE":
        query('DELETE FROM PatrocinioEdicion WHERE IdEdicion=%s', (id,))
        query('DELETE FROM Ediciones WHERE IdEdicion=%s', (id,))
        return _json({"message": "Eliminada"})

# --- HOTELES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def hoteles(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Hoteles WHERE IdHotel=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM Hoteles ORDER BY NombreHotel')])

    if request.method == "POST":
        data = _body(request)
        r = query_one(
            'INSERT INTO Hoteles (NombreHotel, Direccion, Estrellas) VALUES (%s,%s,%s) RETURNING IdHotel',
            (data["NombreHotel"], data.get("Direccion"), data.get("Estrellas")))
        return _json({"id": r["IdHotel"]}, 201)

    if request.method == "PUT":
        data = _body(request)
        query('UPDATE Hoteles SET NombreHotel=%s, Direccion=%s, Estrellas=%s WHERE IdHotel=%s',
              (data["NombreHotel"], data.get("Direccion"), data.get("Estrellas"), id))
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        query('DELETE FROM Alojamientos WHERE IdHotel=%s', (id,))
        query('DELETE FROM Hoteles WHERE IdHotel=%s', (id,))
        return _json({"message": "Eliminado"})

# --- ALOJAMIENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def alojamientos(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Alojamientos WHERE IdAlojamiento=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Alojamientos ORDER BY CheckIn')])

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            r = query_one(
                'INSERT INTO Alojamientos (IdPersonal, IdHotel, IdEdicion, NroHabitacion, CheckIn, CheckOut) '
                'VALUES (%s,%s,%s,%s,%s,%s) RETURNING IdAlojamiento',
                (data["IdPersonal"], data["IdHotel"], id_edicion,
                 data["NroHabitacion"], data["CheckIn"], data["CheckOut"]))
            return _json({"id": r["IdAlojamiento"]}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            query(
                'UPDATE Alojamientos SET IdPersonal=%s, IdHotel=%s, IdEdicion=%s, '
                'NroHabitacion=%s, CheckIn=%s, CheckOut=%s WHERE IdAlojamiento=%s',
                (data["IdPersonal"], data["IdHotel"], id_edicion,
                 data["NroHabitacion"], data["CheckIn"], data["CheckOut"], id))
            return _json({"message": "Actualizado"})
        except Exception as e:
            return _db_error(e)

    if request.method == "DELETE":
        query('DELETE FROM Alojamientos WHERE IdAlojamiento=%s', (id,))
        return _json({"message": "Eliminado"})

# --- TRASLADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def traslados(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Traslados WHERE IdTraslado=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Traslados ORDER BY FechaHora')])

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            r = query_one(
                'INSERT INTO Traslados (IdPersonal, IdEdicion, TipoTraslado, Origen, Destino, FechaHora, NroVuelo) '
                'VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING IdTraslado',
                (data["IdPersonal"], id_edicion, data["TipoTraslado"],
                 data["Origen"], data["Destino"], data["FechaHora"], data.get("NroVuelo")))
            return _json({"id": r["IdTraslado"]}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            query(
                'UPDATE Traslados SET IdPersonal=%s, IdEdicion=%s, TipoTraslado=%s, '
                'Origen=%s, Destino=%s, FechaHora=%s, NroVuelo=%s WHERE IdTraslado=%s',
                (data["IdPersonal"], id_edicion, data["TipoTraslado"],
                 data["Origen"], data["Destino"], data["FechaHora"], data.get("NroVuelo"), id))
            return _json({"message": "Actualizado"})
        except Exception as e:
            return _db_error(e)

    if request.method == "DELETE":
        query('DELETE FROM Traslados WHERE IdTraslado=%s', (id,))
        return _json({"message": "Eliminado"})

# --- PREMIOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def premios(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Premios WHERE IdPremio=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Premios ORDER BY Anio DESC, NombreCategoria')])

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            r = query_one(
                'INSERT INTO Premios (IdCategoria, IdPelicula, IdEdicion) VALUES (%s,%s,%s) RETURNING IdPremio',
                (data["IdCategoria"], data["IdPelicula"], id_edicion))
            return _json({"id": r["IdPremio"]}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            query(
                'UPDATE Premios SET IdCategoria=%s, IdPelicula=%s, IdEdicion=%s WHERE IdPremio=%s',
                (data["IdCategoria"], data["IdPelicula"], id_edicion, id))
            return _json({"message": "Actualizado"})
        except Exception as e:
            return _db_error(e)

    if request.method == "DELETE":
        query('DELETE FROM Premios WHERE IdPremio=%s', (id,))
        return _json({"message": "Eliminado"})

# --- TARIFAS ---
@csrf_exempt
@require_http_methods(["GET"])
def tarifas(request):
    return _json([dict(r) for r in query('SELECT * FROM vw_Tarifas')])

# --- TIPOS ABONO ---
@csrf_exempt
@require_http_methods(["GET"])
def tiposabono(request):
    return _json([dict(r) for r in query('SELECT * FROM vw_TiposAbono')])

# --- COMPETENCIA PELICULA ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def competencia(request):
    if request.method == "GET":
        pelicula_id  = request.GET.get("pelicula")
        categoria_id = request.GET.get("categoria")
        if pelicula_id and categoria_id:
            r = query_one(
                'SELECT * FROM vw_Competencia WHERE IdPelicula=%s AND IdCategoria=%s',
                (pelicula_id, categoria_id))
            return _json(r) if r else _not_found()
        if pelicula_id:
            return _json([dict(r) for r in query(
                'SELECT * FROM vw_Competencia WHERE IdPelicula=%s ORDER BY NombreCategoria',
                (pelicula_id,))])
        if categoria_id:
            return _json([dict(r) for r in query(
                'SELECT * FROM vw_Competencia WHERE IdCategoria=%s ORDER BY Titulo',
                (categoria_id,))])
        return _json([dict(r) for r in query(
            'SELECT * FROM vw_Competencia ORDER BY Titulo, NombreCategoria')])

    if request.method == "POST":
        data = _body(request)
        id_edicion = data.get("IdEdicion") or _current_edicion_id()
        r = query_one(
            'INSERT INTO CompetenciaPelicula (IdPelicula, IdCategoria, IdEdicion) VALUES (%s,%s,%s) RETURNING IdPelicula',
            (data["IdPelicula"], data["IdCategoria"], id_edicion))
        return _json({"id": r["IdPelicula"]}, 201)

    if request.method == "DELETE":
        pelicula_id  = request.GET.get("pelicula")
        categoria_id = request.GET.get("categoria")
        query('DELETE FROM CompetenciaPelicula WHERE IdPelicula=%s AND IdCategoria=%s',
              (pelicula_id, categoria_id))
        return _json({"message": "Eliminada de competencia"})

# --- REPORTES ---
@csrf_exempt
@require_http_methods(["GET"])
def reporte_ranking(request):
    try:
        return _json([dict(r) for r in query('SELECT * FROM fn_reporte_ranking()')])
    except Exception as e:
        return _db_error(e)

@csrf_exempt
@require_http_methods(["GET"])
def reporte_premiacion(request):
    id_edicion = request.GET.get("id_edicion")
    try:
        if id_edicion:
            rows = query('SELECT * FROM fn_reporte_premiacion(%s)', (id_edicion,))
        else:
            rows = query('SELECT * FROM fn_reporte_premiacion()')
        return _json([dict(r) for r in rows])
    except Exception as e:
        return _db_error(e)

@csrf_exempt
@require_http_methods(["GET"])
def reporte_financiero(request):
    try:
        data = [dict(r) for r in query('SELECT * FROM fn_reporte_financiero()')]
        total_general = sum(r["Subtotal"] for r in data)
        return _json({
            "detalle": data,
            "totalGeneral": total_general,
            "totalPorTipoVenta": {
                tv: sum(r["Subtotal"] for r in data if r["TipoVenta"] == tv)
                for tv in {r["TipoVenta"] for r in data}
            }
        })
    except Exception as e:
        return _db_error(e)

@csrf_exempt
@require_http_methods(["GET"])
def reporte_ocupacion(request):
    try:
        return _json([dict(r) for r in query('SELECT * FROM fn_reporte_ocupacion()')])
    except Exception as e:
        return _db_error(e)

@csrf_exempt
@require_http_methods(["GET"])
def reporte_ventas_edicion(request, id):
    ent = query_one(
        'SELECT COUNT(*) AS Cantidad, COALESCE(SUM(t.precio), 0) AS Total '
        'FROM entradas e JOIN tarifas t ON t.idtarifa = e.idtarifa')
    abo = query_one(
        'SELECT COUNT(*) AS Cantidad, COALESCE(SUM(ta.precio), 0) AS Total '
        'FROM abonos a JOIN tiposabono ta ON ta.idtipoabono = a.idtipoabono '
        'WHERE a.pagado = TRUE')
    return _json({
        "entradas": ent if ent else {"Cantidad": 0, "Total": 0},
        "abonos":   abo if abo else {"Cantidad": 0, "Total": 0}
    })

# --- ROLES PELICULA ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def roles_pelicula(request):
    if request.method == "GET":
        personal_id = request.GET.get("personal")
        pelicula_id = request.GET.get("pelicula")
        if personal_id:
            return _json([dict(r) for r in query(
                'SELECT * FROM vw_RolesPelicula WHERE IdPersonal=%s', (personal_id,))])
        if pelicula_id:
            return _json([dict(r) for r in query(
                'SELECT * FROM vw_RolesPelicula WHERE IdPelicula=%s', (pelicula_id,))])
        return _json([dict(r) for r in query(
            'SELECT * FROM vw_RolesPelicula ORDER BY Pelicula, Personal')])

    if request.method == "POST":
        data = _body(request)
        query('INSERT INTO RolesPelicula (IdPersonal, IdPelicula, Rol) VALUES (%s,%s,%s)',
              (data["IdPersonal"], data["IdPelicula"], data["Rol"]))
        return _json({"message": "Rol registrado"}, 201)

    if request.method == "DELETE":
        personal_id = request.GET.get("personal")
        pelicula_id = request.GET.get("pelicula")
        rol         = request.GET.get("rol")
        query('DELETE FROM RolesPelicula WHERE IdPersonal=%s AND IdPelicula=%s AND Rol=%s',
              (personal_id, pelicula_id, rol))
        return _json({"message": "Rol eliminado"})