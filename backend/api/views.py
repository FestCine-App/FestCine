import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from config.database import query, query_one

def _json(data, status=200):
    return JsonResponse(data, safe=False, status=status)

def _body(request):
    return json.loads(request.body) if request.body else {}

def _not_found(msg="No encontrado"):
    return _json({"error": msg}, 404)

def _error(msg, status=400):
    return _json({"error": msg}, status)

# --- PELICULAS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def peliculas(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Peliculas WHERE IdPelicula=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Peliculas ORDER BY Titulo')])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Peliculas (Titulo,AnioProd,Duracion,PaisOrigen,Sinopsis,Clasificacion,Formato,Estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING IdPelicula',
            (data["Titulo"], data["AnioProd"], data["Duracion"], data["PaisOrigen"],
             data.get("Sinopsis"), data["Clasificacion"], data["Formato"], data.get("Estado", "Postulada")))
        pid = r["IdPelicula"]
        for g in data.get("generos", []):
            query('INSERT INTO PeliculaGenero (IdPelicula,IdGenero) VALUES (%s,%s)', (pid, g))
        return _json({"id": pid}, 201)

    if request.method == "PUT":
        data = _body(request)
        query('UPDATE Peliculas SET Titulo=%s,AnioProd=%s,Duracion=%s,PaisOrigen=%s,Sinopsis=%s,Clasificacion=%s,Formato=%s,Estado=%s WHERE IdPelicula=%s',
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
            rows = query('SELECT * FROM fn_call_programarproyeccion(%s,%s,%s,%s,%s)',
                (data["IdPelicula"], data["IdSala"], data["IdEdicion"], data["FechaHora"], data.get("TieneQA", False)))
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
            r = query_one('SELECT * FROM Asistentes WHERE IdAsistente=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Asistentes ORDER BY Nombre')])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Asistentes (Nombre, Email, Telefono, TipoAsistente) VALUES (%s,%s,%s,%s) RETURNING IdAsistente',
            (data["Nombre"], data["Email"], data.get("Telefono"), data.get("TipoAsistente", "General")))
        return _json({"id": r["IdAsistente"]}, 201)

# --- ENTRADAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def entradas(request):
    if request.method == "GET":
        rows = query('SELECT e.*, a.Nombre AS Asistente, p.Titulo AS Pelicula, pr.FechaHora FROM Entradas e JOIN Asistentes a ON a.IdAsistente = e.IdAsistente LEFT JOIN Proyecciones pr ON pr.IdProyeccion = e.IdProyeccion LEFT JOIN Peliculas p ON p.IdPelicula = pr.IdPelicula ORDER BY e.FechaCompra DESC')
        return _json([dict(r) for r in rows])

    if request.method == "POST":
        data = _body(request)
        try:
            rows = query('SELECT * FROM fn_call_comprarentrada(%s,%s,%s)',
                (int(data["IdAsistente"]), int(data["IdProyeccion"]), int(data["IdTarifa"])))
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
        rows = query('SELECT * FROM vw_Abonos')
        return _json([dict(r) for r in rows])

    if request.method == "POST":
        data = _body(request)
        try:
            rows = query('SELECT * FROM fn_call_venderabono(%s,%s,%s,%s)',
                (data["IdAsistente"], data["IdTipoAbono"], data["IdEdicion"], data.get("PagoExitoso", True)))
            msg = rows[0]["Respuesta"] if rows else ""
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
        r = query_one('INSERT INTO Sedes (NombreSede, Direccion, Ciudad, SitioWeb) VALUES (%s,%s,%s,%s) RETURNING IdSede',
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
        r = query_one('INSERT INTO Salas (NombreSala, Capacidad, IdSede) VALUES (%s,%s,%s) RETURNING IdSala',
            (data["NombreSala"], data["Capacidad"], data["IdSede"]))
        return _json({"id": r["IdSala"]}, 201)

# --- EVENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def eventos(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM vw_Eventos WHERE IdEvento=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM vw_Eventos ORDER BY FechaHora')])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO EventosParalelos (IdEdicion, NombreEvento, TipoEvento, FechaHora, Aforo, CostoInscripcion) VALUES (%s,%s,%s,%s,%s,%s) RETURNING IdEvento',
            (data["IdEdicion"], data["NombreEvento"], data["TipoEvento"], data["FechaHora"],
             data["Aforo"], data.get("CostoInscripcion", 0)))
        eid = r["IdEvento"]
        for p in data.get("expositores", []):
            query('INSERT INTO ExpositorEvento (IdEvento, IdPersonal) VALUES (%s,%s)', (eid, p))
        return _json({"id": eid}, 201)

# --- GENEROS ---
@csrf_exempt
@require_http_methods(["GET"])
def generos(request):
    return _json([dict(r) for r in query('SELECT * FROM Generos ORDER BY NombreGenero')])

# --- PERSONAL ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def personal(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Personal WHERE IdPersonal=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM Personal ORDER BY Nombre')])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Personal (Nombre, Biografia, Email, Telefono, Nacionalidad) VALUES (%s,%s,%s,%s,%s) RETURNING IdPersonal',
            (data["Nombre"], data.get("Biografia"), data.get("Email"), data.get("Telefono"), data.get("Nacionalidad")))
        return _json({"id": r["IdPersonal"]}, 201)

# --- CATEGORIAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def categorias(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Categorias WHERE IdCategoria=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM Categorias ORDER BY NombreCategoria')])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Categorias (NombreCategoria, Descripcion) VALUES (%s,%s) RETURNING IdCategoria',
            (data["NombreCategoria"], data.get("Descripcion")))
        return _json({"id": r["IdCategoria"]}, 201)

# --- JURADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def jurados(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM MiembrosJurado WHERE IdMiembro=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM MiembrosJurado ORDER BY Nombre')])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO MiembrosJurado (Nombre, Profesion, Pais, Email) VALUES (%s,%s,%s,%s) RETURNING IdMiembro',
            (data["Nombre"], data.get("Profesion"), data.get("Pais"), data.get("Email")))
        return _json({"id": r["IdMiembro"]}, 201)

# --- EVALUACIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def evaluaciones(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT ev.*, m.Nombre AS Jurado, p.Titulo AS Pelicula, c.NombreCategoria AS Categoria, ed.Anio, ed.NombreEdicion FROM Evaluaciones ev JOIN MiembrosJurado m ON m.IdMiembro = ev.IdMiembro JOIN Peliculas p ON p.IdPelicula = ev.IdPelicula JOIN Categorias c ON c.IdCategoria = ev.IdCategoria JOIN Ediciones ed ON ed.IdEdicion = ev.IdEdicion WHERE ev.IdEvaluacion=%s', (id,))
            return _json(r) if r else _not_found()
        rows = query('SELECT ev.*, m.Nombre AS Jurado, p.Titulo AS Pelicula, c.NombreCategoria AS Categoria, ed.Anio, ed.NombreEdicion FROM Evaluaciones ev JOIN MiembrosJurado m ON m.IdMiembro = ev.IdMiembro JOIN Peliculas p ON p.IdPelicula = ev.IdPelicula JOIN Categorias c ON c.IdCategoria = ev.IdCategoria JOIN Ediciones ed ON ed.IdEdicion = ev.IdEdicion ORDER BY ev.IdEvaluacion')
        return _json([dict(r) for r in rows])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Evaluaciones (IdMiembro, IdPelicula, IdCategoria, IdEdicion, Puntuacion, Comentario) VALUES (%s,%s,%s,%s,%s,%s) RETURNING IdEvaluacion',
            (data["IdMiembro"], data["IdPelicula"], data["IdCategoria"], data["IdEdicion"], data["Puntuacion"], data.get("Comentario")))
        return _json({"id": r["IdEvaluacion"]}, 201)

# --- PATROCINADORES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def patrocinadores(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Patrocinadores WHERE IdPatrocinador=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM Patrocinadores ORDER BY NombreEmpresa')])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Patrocinadores (NombreEmpresa, Contacto, Email, RedesSociales) VALUES (%s,%s,%s,%s) RETURNING IdPatrocinador',
            (data["NombreEmpresa"], data.get("Contacto"), data.get("Email"), data.get("RedesSociales")))
        return _json({"id": r["IdPatrocinador"]}, 201)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def patrocinios(request):
    if request.method == "GET":
        rows = query('SELECT pe.*, p.NombreEmpresa, e.NombreEdicion, e.Anio FROM PatrocinioEdicion pe JOIN Patrocinadores p ON p.IdPatrocinador = pe.IdPatrocinador JOIN Ediciones e ON e.IdEdicion = pe.IdEdicion ORDER BY e.Anio DESC')
        return _json([dict(r) for r in rows])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO PatrocinioEdicion (IdPatrocinador, IdEdicion, TipoAporte, Monto, DescripcionAporte) VALUES (%s,%s,%s,%s,%s) RETURNING IdPatrocinio',
            (data["IdPatrocinador"], data["IdEdicion"], data["TipoAporte"], data.get("Monto"), data.get("DescripcionAporte")))
        return _json({"id": r["IdPatrocinio"]}, 201)

# --- EDICIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def ediciones(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Ediciones WHERE IdEdicion=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM Ediciones ORDER BY Anio DESC')])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Ediciones (Anio, NombreEdicion, FechaInicio, FechaFin) VALUES (%s,%s,%s,%s) RETURNING IdEdicion',
            (data["Anio"], data["NombreEdicion"], data["FechaInicio"], data["FechaFin"]))
        return _json({"id": r["IdEdicion"]}, 201)

# --- HOTELES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def hoteles(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT * FROM Hoteles WHERE IdHotel=%s', (id,))
            return _json(r) if r else _not_found()
        return _json([dict(r) for r in query('SELECT * FROM Hoteles ORDER BY NombreHotel')])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Hoteles (NombreHotel, Direccion, Estrellas) VALUES (%s,%s,%s) RETURNING IdHotel',
            (data["NombreHotel"], data.get("Direccion"), data.get("Estrellas")))
        return _json({"id": r["IdHotel"]}, 201)

# --- ALOJAMIENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def alojamientos(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT a.*, p.Nombre AS Personal, h.NombreHotel FROM Alojamientos a JOIN Personal p ON p.IdPersonal = a.IdPersonal JOIN Hoteles h ON h.IdHotel = a.IdHotel WHERE a.IdAlojamiento=%s', (id,))
            return _json(r) if r else _not_found()
        rows = query('SELECT a.*, p.Nombre AS Personal, h.NombreHotel FROM Alojamientos a JOIN Personal p ON p.IdPersonal = a.IdPersonal JOIN Hoteles h ON h.IdHotel = a.IdHotel ORDER BY a.CheckIn')
        return _json([dict(r) for r in rows])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Alojamientos (IdPersonal, IdHotel, IdEdicion, NroHabitacion, CheckIn, CheckOut) VALUES (%s,%s,%s,%s,%s,%s) RETURNING IdAlojamiento',
            (data["IdPersonal"], data["IdHotel"], data["IdEdicion"], data["NroHabitacion"], data["CheckIn"], data["CheckOut"]))
        return _json({"id": r["IdAlojamiento"]}, 201)

# --- TRASLADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def traslados(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT t.*, p.Nombre AS Personal FROM Traslados t JOIN Personal p ON p.IdPersonal = t.IdPersonal WHERE t.IdTraslado=%s', (id,))
            return _json(r) if r else _not_found()
        rows = query('SELECT t.*, p.Nombre AS Personal FROM Traslados t JOIN Personal p ON p.IdPersonal = t.IdPersonal ORDER BY t.FechaHora')
        return _json([dict(r) for r in rows])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Traslados (IdPersonal, IdEdicion, TipoTraslado, Origen, Destino, FechaHora, NroVuelo) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING IdTraslado',
            (data["IdPersonal"], data["IdEdicion"], data["TipoTraslado"], data["Origen"], data["Destino"], data["FechaHora"], data.get("NroVuelo")))
        return _json({"id": r["IdTraslado"]}, 201)

# --- PREMIOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def premios(request, id=None):
    if request.method == "GET":
        if id:
            r = query_one('SELECT pre.*, c.NombreCategoria, p.Titulo AS Pelicula, e.Anio, e.NombreEdicion FROM Premios pre JOIN Categorias c ON c.IdCategoria = pre.IdCategoria JOIN Peliculas p ON p.IdPelicula = pre.IdPelicula JOIN Ediciones e ON e.IdEdicion = pre.IdEdicion WHERE pre.IdPremio=%s', (id,))
            return _json(r) if r else _not_found()
        rows = query('SELECT pre.*, c.NombreCategoria, p.Titulo AS Pelicula, e.Anio, e.NombreEdicion FROM Premios pre JOIN Categorias c ON c.IdCategoria = pre.IdCategoria JOIN Peliculas p ON p.IdPelicula = pre.IdPelicula JOIN Ediciones e ON e.IdEdicion = pre.IdEdicion ORDER BY e.Anio DESC, c.NombreCategoria')
        return _json([dict(r) for r in rows])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO Premios (IdCategoria, IdPelicula, IdEdicion) VALUES (%s,%s,%s) RETURNING IdPremio',
            (data["IdCategoria"], data["IdPelicula"], data["IdEdicion"]))
        return _json({"id": r["IdPremio"]}, 201)

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
@require_http_methods(["GET", "POST"])
def competencia(request):
    if request.method == "GET":
        pelicula_id = request.GET.get("pelicula")
        categoria_id = request.GET.get("categoria")
        edicion_id = request.GET.get("edicion")
        if pelicula_id and categoria_id and edicion_id:
            r = query_one('SELECT cp.*, p.Titulo, c.NombreCategoria, e.Anio, e.NombreEdicion FROM CompetenciaPelicula cp JOIN Peliculas p ON p.IdPelicula = cp.IdPelicula JOIN Categorias c ON c.IdCategoria = cp.IdCategoria JOIN Ediciones e ON e.IdEdicion = cp.IdEdicion WHERE cp.IdPelicula=%s AND cp.IdCategoria=%s AND cp.IdEdicion=%s', (pelicula_id, categoria_id, edicion_id))
            return _json(r) if r else _not_found()
        rows = query('SELECT cp.*, p.Titulo, c.NombreCategoria, e.Anio, e.NombreEdicion FROM CompetenciaPelicula cp JOIN Peliculas p ON p.IdPelicula = cp.IdPelicula JOIN Categorias c ON c.IdCategoria = cp.IdCategoria JOIN Ediciones e ON e.IdEdicion = cp.IdEdicion ORDER BY p.Titulo, c.NombreCategoria')
        return _json([dict(r) for r in rows])

    if request.method == "POST":
        data = _body(request)
        r = query_one('INSERT INTO CompetenciaPelicula (IdPelicula, IdCategoria, IdEdicion) VALUES (%s,%s,%s) RETURNING IdPelicula',
            (data["IdPelicula"], data["IdCategoria"], data["IdEdicion"]))
        return _json({"id": r["IdPelicula"]}, 201)

# --- REPORTES ---
@csrf_exempt
@require_http_methods(["GET"])
def reporte_ranking(request):
    id_edicion = request.GET.get("id_edicion")
    if id_edicion:
        rows = query('SELECT p.Titulo, COUNT(e.IdEntrada) AS Asistentes, SUM(s.Capacidad) AS CapacidadTotal, ROUND(COUNT(e.IdEntrada) * 100.0 / NULLIF(SUM(s.Capacidad), 0), 2) AS PctOcupacion FROM Peliculas p INNER JOIN Proyecciones pr ON pr.IdPelicula = p.IdPelicula INNER JOIN Salas s ON s.IdSala = pr.IdSala LEFT JOIN Entradas e ON e.IdProyeccion = pr.IdProyeccion WHERE pr.IdEdicion = %s GROUP BY p.Titulo ORDER BY Asistentes DESC', (id_edicion,))
    else:
        rows = query('SELECT p.Titulo, COUNT(e.IdEntrada) AS Asistentes, SUM(s.Capacidad) AS CapacidadTotal, ROUND(COUNT(e.IdEntrada) * 100.0 / NULLIF(SUM(s.Capacidad), 0), 2) AS PctOcupacion FROM Peliculas p INNER JOIN Proyecciones pr ON pr.IdPelicula = p.IdPelicula INNER JOIN Salas s ON s.IdSala = pr.IdSala LEFT JOIN Entradas e ON e.IdProyeccion = pr.IdProyeccion GROUP BY p.Titulo ORDER BY Asistentes DESC')
    return _json([dict(r) for r in rows])

@csrf_exempt
@require_http_methods(["GET"])
def reporte_premiacion(request):
    id_edicion = request.GET.get("id_edicion")
    if id_edicion:
        rows = query('SELECT c.NombreCategoria, p.Titulo AS PeliculaGanadora, ROUND(AVG(ev.Puntuacion), 2) AS PromedioJurado, e.Anio FROM Premios pre INNER JOIN Categorias c ON c.IdCategoria = pre.IdCategoria INNER JOIN Peliculas p ON p.IdPelicula = pre.IdPelicula INNER JOIN Ediciones e ON e.IdEdicion = pre.IdEdicion INNER JOIN Evaluaciones ev ON ev.IdPelicula = pre.IdPelicula AND ev.IdCategoria = pre.IdCategoria AND ev.IdEdicion = pre.IdEdicion WHERE pre.IdEdicion = %s GROUP BY c.NombreCategoria, p.Titulo, e.Anio ORDER BY c.NombreCategoria', (id_edicion,))
    else:
        rows = query('SELECT c.NombreCategoria, p.Titulo AS PeliculaGanadora, ROUND(AVG(ev.Puntuacion), 2) AS PromedioJurado, e.Anio FROM Premios pre INNER JOIN Categorias c ON c.IdCategoria = pre.IdCategoria INNER JOIN Peliculas p ON p.IdPelicula = pre.IdPelicula INNER JOIN Ediciones e ON e.IdEdicion = pre.IdEdicion INNER JOIN Evaluaciones ev ON ev.IdPelicula = pre.IdPelicula AND ev.IdCategoria = pre.IdCategoria AND ev.IdEdicion = pre.IdEdicion GROUP BY c.NombreCategoria, p.Titulo, e.Anio ORDER BY c.NombreCategoria')
    return _json([dict(r) for r in rows])

@csrf_exempt
@require_http_methods(["GET"])
def reporte_financiero(request):
    id_edicion = request.GET.get("id_edicion")
    if id_edicion:
        rows = query("SELECT t.NombreTarifa, COUNT(e.IdEntrada) AS Cantidad, SUM(t.Precio) AS Subtotal FROM Entradas e INNER JOIN Proyecciones pr ON pr.IdProyeccion = e.IdProyeccion INNER JOIN Tarifas t ON t.IdTarifa = e.IdTarifa WHERE pr.IdEdicion = %s GROUP BY t.NombreTarifa ORDER BY Subtotal DESC", (id_edicion,))
    else:
        rows = query("SELECT t.NombreTarifa, COUNT(e.IdEntrada) AS Cantidad, SUM(t.Precio) AS Subtotal FROM Entradas e INNER JOIN Tarifas t ON t.IdTarifa = e.IdTarifa GROUP BY t.NombreTarifa ORDER BY Subtotal DESC")
    return _json([dict(r) for r in rows])

@csrf_exempt
@require_http_methods(["GET"])
def reporte_ocupacion(request):
    rows = query('SELECT s.NombreSala, se.NombreSede, s.Capacidad, COUNT(e.IdEntrada) AS EntradasVendidas, ROUND(COUNT(e.IdEntrada) * 100.0 / NULLIF(s.Capacidad, 0), 2) AS PorcentajeOcupacion FROM Salas s JOIN Sedes se ON se.IdSede = s.IdSede LEFT JOIN Proyecciones pr ON pr.IdSala = s.IdSala LEFT JOIN Entradas e ON e.IdProyeccion = pr.IdProyeccion GROUP BY s.IdSala, se.NombreSede ORDER BY PorcentajeOcupacion DESC')
    return _json([dict(r) for r in rows])

@csrf_exempt
@require_http_methods(["GET"])
def reporte_ventas_edicion(request, id):
    ent = query_one('SELECT COUNT(*) AS Cantidad, SUM(t.Precio) AS Total FROM Entradas e JOIN Tarifas t ON t.IdTarifa = e.IdTarifa JOIN Proyecciones pr ON pr.IdProyeccion = e.IdProyeccion WHERE pr.IdEdicion = %s', (id,))
    abo = query_one('SELECT COUNT(*) AS Cantidad, SUM(ta.Precio) AS Total FROM Abonos a JOIN TiposAbono ta ON ta.IdTipoAbono = a.IdTipoAbono WHERE a.Pagado = TRUE AND a.IdEdicion = %s', (id,))
    return _json({"entradas": ent if ent else {"Cantidad": 0, "Total": 0}, "abonos": abo if abo else {"Cantidad": 0, "Total": 0}})
