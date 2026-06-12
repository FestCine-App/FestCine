import json
import random
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection

def _json(data, status=200):
    return JsonResponse(data, safe=False, status=status)

def _body(request):
    return json.loads(request.body) if request.body else {}

def _not_found(msg="No encontrado"):
    return _json({"error": msg}, 404)

def _error(msg, status=400):
    return _json({"error": msg}, status)

COL_MAP = {'idgenero': 'IdGenero', 'nombregenero': 'NombreGenero', 'idpelicula': 'IdPelicula', 'titulo': 'Titulo', 'anioprod': 'AnioProd', 'duracion': 'Duracion', 'paisorigen': 'PaisOrigen', 'sinopsis': 'Sinopsis', 'clasificacion': 'Clasificacion', 'formato': 'Formato', 'estado': 'Estado', 'idpersonal': 'IdPersonal', 'nombre': 'Nombre', 'biografia': 'Biografia', 'email': 'Email', 'telefono': 'Telefono', 'nacionalidad': 'Nacionalidad', 'rol': 'Rol', 'idedicion': 'IdEdicion', 'anio': 'Anio', 'nombreedicion': 'NombreEdicion', 'fechainicio': 'FechaInicio', 'fechafin': 'FechaFin', 'idsede': 'IdSede', 'nombresede': 'NombreSede', 'direccion': 'Direccion', 'ciudad': 'Ciudad', 'sitioweb': 'SitioWeb', 'idsala': 'IdSala', 'nombresala': 'NombreSala', 'capacidad': 'Capacidad', 'idproyeccion': 'IdProyeccion', 'fechahora': 'FechaHora', 'tieneqa': 'TieneQA', 'aforodisponible': 'AforoDisponible', 'idevento': 'IdEvento', 'nombreevento': 'NombreEvento', 'tipoevento': 'TipoEvento', 'aforo': 'Aforo', 'costoinscripcion': 'CostoInscripcion', 'idcategoria': 'IdCategoria', 'nombrecategoria': 'NombreCategoria', 'descripcion': 'Descripcion', 'idmiembro': 'IdMiembro', 'profesion': 'Profesion', 'pais': 'Pais', 'idevaluacion': 'IdEvaluacion', 'puntuacion': 'Puntuacion', 'comentario': 'Comentario', 'idpremio': 'IdPremio', 'idasistente': 'IdAsistente', 'tipoasistente': 'TipoAsistente', 'idtarifa': 'IdTarifa', 'nombretarifa': 'NombreTarifa', 'precio': 'Precio', 'identrada': 'IdEntrada', 'fechacompra': 'FechaCompra', 'idtipoabono': 'IdTipoAbono', 'nombreabono': 'NombreAbono', 'idabono': 'IdAbono', 'codigoacceso': 'CodigoAcceso', 'pagado': 'Pagado', 'idhotel': 'IdHotel', 'nombrehotel': 'NombreHotel', 'estrellas': 'Estrellas', 'idalojamiento': 'IdAlojamiento', 'nrohabitacion': 'NroHabitacion', 'checkin': 'CheckIn', 'checkout': 'CheckOut', 'idtraslado': 'IdTraslado', 'tipotraslado': 'TipoTraslado', 'origen': 'Origen', 'destino': 'Destino', 'nrovuelo': 'NroVuelo', 'idpatrocinador': 'IdPatrocinador', 'nombreempresa': 'NombreEmpresa', 'contacto': 'Contacto', 'redessociales': 'RedesSociales', 'idpatrocinio': 'IdPatrocinio', 'tipoaporte': 'TipoAporte', 'monto': 'Monto', 'descripcionaporte': 'DescripcionAporte', 'generos': 'Generos', 'edicionnombre': 'EdicionNombre'}

def query_view(sql, params=None):
    with connection.cursor() as cur:
        cur.execute(sql, params)
        if cur.description:
            columns = [COL_MAP.get(col[0].lower(), col[0]) for col in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        return []

def call_procedure(proc_name, params=None):
    with connection.cursor() as cur:
        try:
            if params is None:
                params = []
            placeholders = ", ".join(["%s"] * len(params))
            
            if proc_name.startswith("fn_call_"):
                cur.execute(f"SELECT respuesta FROM {proc_name}({placeholders})", params)
                row = cur.fetchone()
                return {"success": True, "message": row[0] if row else "OK"}
            else:
                cur.execute(f"CALL {proc_name}({placeholders})", params)
                return {"success": True, "message": "Operación completada"}
        except Exception as e:
            return {"success": False, "error": str(e).split('\n')[0]}

def handle_crud(request, proc_create, proc_update, proc_delete, create_params_fn, update_params_fn, id=None):
    if request.method == "POST":
        data = _body(request)
        res = call_procedure(proc_create, create_params_fn(data))
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 201 if res["success"] else 400)
    if request.method == "PUT":
        data = _body(request)
        res = call_procedure(proc_update, update_params_fn(id, data))
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 200 if res["success"] else 400)
    if request.method == "DELETE":
        res = call_procedure(proc_delete, [id])
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 200 if res["success"] else 400)


# --- PELICULAS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def peliculas(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_admin_peliculas WHERE idpelicula = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_admin_peliculas"))
    
    return handle_crud(
        request, "registrarpelicula", "actualizarpelicula", "eliminarpelicula",
        lambda d: [d["Titulo"], d["AnioProd"], d["Duracion"], d["PaisOrigen"], d.get("Sinopsis"), d["Clasificacion"], d["Formato"], d.get("Estado", "Postulada"), d.get("generos", []), d.get("IdEdicion"), d.get("categorias", [])],
        lambda i, d: [i, d["Titulo"], d["AnioProd"], d["Duracion"], d["PaisOrigen"], d.get("Sinopsis"), d["Clasificacion"], d["Formato"], d.get("Estado"), d.get("generos", []), d.get("IdEdicion"), d.get("categorias", [])],
        id
    )

# --- PROYECCIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def proyecciones(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_proyecciones WHERE idproyeccion = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_proyecciones ORDER BY fechahora"))

    if request.method == "POST":
        data = _body(request)
        # Using fn_call_programarproyeccion to capture ID and Message
        res = call_procedure("fn_call_programarproyeccion", [data["IdPelicula"], data["IdSala"], data.get("IdEdicion"), data["FechaHora"], data.get("TieneQA", False)])
        if res["success"]:
            return _json({"message": res["message"]}, 201)
        return _error(res["error"], 409 if "Control de Agenda" in res["error"] else 400)

    if request.method == "DELETE":
        res = call_procedure("eliminarproyeccion", [id])
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 200 if res["success"] else 400)

# --- ASISTENTES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def asistentes(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_asistentes WHERE idasistente = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_asistentes ORDER BY nombre"))

    if request.method == "POST":
        data = _body(request)
        res = call_procedure("registrarasistente", [data["Nombre"], data["Email"], data.get("Telefono"), data.get("TipoAsistente", "General")])
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 201 if res["success"] else 400)

# --- ENTRADAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def entradas(request):
    if request.method == "GET":
        return _json(query_view("SELECT * FROM vw_entradas ORDER BY fechacompra DESC"))

    if request.method == "POST":
        data = _body(request)
        if data.get("IdProyeccion"):
            res = call_procedure("fn_call_comprarentrada", [data["IdAsistente"], data["IdProyeccion"], data["IdTarifa"]])
        elif data.get("IdEvento"):
            res = call_procedure("fn_call_comprarentradaevento", [data["IdAsistente"], data["IdEvento"], data["IdTarifa"]])
        else:
            return _error("Debe especificar una proyeccion o un evento")
        
        if res["success"] and not res["message"].lower().startswith("error"):
            return _json({"message": res["message"]}, 201)
        return _error(res.get("error") or res["message"], 400)

# --- ABONOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def abonos(request):
    if request.method == "GET":
        return _json(query_view("SELECT * FROM vw_abonos ORDER BY fechacompra DESC"))

    if request.method == "POST":
        data = _body(request)
        res = call_procedure("fn_call_venderabono", [data["IdAsistente"], data["IdTipoAbono"], data.get("IdEdicion"), data.get("PagoExitoso", True)])
        if res["success"] and not res["message"].lower().startswith("error"):
            return _json({"message": res["message"]}, 201)
        return _error(res.get("error") or res["message"], 400)

# --- SEDES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def sedes(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_sedes WHERE idsede = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_sedes ORDER BY nombresede"))
        
    return handle_crud(
        request, "registrarsede", "actualizarsede", "eliminarsede",
        lambda d: [d["NombreSede"], d.get("Direccion"), d.get("Ciudad"), d.get("SitioWeb")],
        lambda i, d: [i, d["NombreSede"], d.get("Direccion"), d.get("Ciudad"), d.get("SitioWeb")],
        id
    )

# --- SALAS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def salas(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_salas WHERE idsala = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_salas ORDER BY nombresede, nombresala"))
        
    return handle_crud(
        request, "registrarsala", "actualizarsala", "eliminarsala",
        lambda d: [d["NombreSala"], d["Capacidad"], d["IdSede"]],
        lambda i, d: [i, d["NombreSala"], d["Capacidad"], d["IdSede"]],
        id
    )

# --- EVENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def eventos(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_eventos WHERE idevento = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_eventos ORDER BY fechahora"))

    return handle_crud(
        request, "registrarevento", "actualizarevento", "eliminarevento",
        lambda d: [d.get("IdEdicion"), d["NombreEvento"], d["TipoEvento"], d["FechaHora"], d["Aforo"], d.get("CostoInscripcion", 0), d.get("expositores", [])],
        lambda i, d: [i, d["NombreEvento"], d["TipoEvento"], d["FechaHora"], d["Aforo"], d.get("CostoInscripcion", 0), d.get("expositores", [])],
        id
    )

# --- GENEROS ---
@csrf_exempt
@require_http_methods(["GET"])
def generos(request):
    return _json(query_view("SELECT * FROM vw_generos ORDER BY nombregenero"))

# --- PERSONAL ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def personal(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_personal WHERE idpersonal = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_personal ORDER BY nombre"))

    return handle_crud(
        request, "registrarpersonal", "actualizarpersonal", "eliminarpersonal",
        lambda d: [d["Nombre"], d.get("Biografia"), d.get("Email"), d.get("Telefono"), d.get("Nacionalidad")],
        lambda i, d: [i, d["Nombre"], d.get("Biografia"), d.get("Email"), d.get("Telefono"), d.get("Nacionalidad")],
        id
    )

# --- CATEGORIAS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def categorias(request, id=None):
    if request.method == "GET":
        jurado_id = request.GET.get('jurado')
        categoria_id = request.GET.get('categoria')
        
        if jurado_id:
            return _json(query_view("SELECT * FROM vw_categoriasporjurado WHERE idmiembro = %s ORDER BY nombrecategoria", [jurado_id]))
        if categoria_id:
            id_edicion = request.GET.get("id_edicion")
            if id_edicion:
                return _json(query_view("SELECT * FROM vw_peliculasporcategoria WHERE idcategoria = %s AND idedicion = %s ORDER BY titulo", [categoria_id, id_edicion]))
            return _json(query_view("SELECT * FROM vw_peliculasporcategoria WHERE idcategoria = %s ORDER BY titulo", [categoria_id]))
            
        if id:
            rows = query_view("SELECT * FROM Categorias WHERE idcategoria = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM Categorias ORDER BY nombrecategoria"))

    return handle_crud(
        request, "registrarcategoria", "actualizarcategoria", "eliminarcategoria",
        lambda d: [d["NombreCategoria"], d.get("Descripcion")],
        lambda i, d: [i, d["NombreCategoria"], d.get("Descripcion")],
        id
    )

# --- JURADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def jurados(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_miembrosjurado WHERE idmiembro = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_miembrosjurado ORDER BY nombre"))

    return handle_crud(
        request, "registrarjurado", "actualizarjurado", "eliminarjurado",
        lambda d: [d["Nombre"], d.get("Profesion"), d.get("Pais"), d.get("Email"), d.get("IdEdicion")],
        lambda i, d: [i, d["Nombre"], d.get("Profesion"), d.get("Pais"), d.get("Email"), d.get("IdEdicion")],
        id
    )

# --- JURADO ASIGNACIONES ---
@csrf_exempt
@require_http_methods(["GET"])
def jurados_asignaciones(request):
    id_jurado = request.GET.get("id_jurado")
    id_edicion = request.GET.get("id_edicion")
    if not id_jurado or not id_edicion:
        return _error("Faltan parámetros id_jurado e id_edicion")
    
    rows = query_view("""
        SELECT c.idpelicula AS "IdPelicula", c.titulo AS "Titulo", c.idcategoria AS "IdCategoria", c.nombrecategoria AS "NombreCategoria",
               (e.idevaluacion IS NOT NULL) AS "Evaluada", e.puntuacion AS "Puntuacion", e.idevaluacion AS "IdEvaluacion"
        FROM vw_competencia c
        INNER JOIN juradocategoria jc ON jc.idcategoria = c.idcategoria AND jc.idmiembro = %s
        LEFT JOIN evaluaciones e ON e.idpelicula = c.idpelicula AND e.idcategoria = c.idcategoria AND e.idedicion = c.idedicion AND e.idmiembro = %s
        WHERE c.idedicion = %s
        ORDER BY c.nombrecategoria, c.titulo
    """, [id_jurado, id_jurado, id_edicion])
    return _json(rows)

# --- JURADO CATEGORIAS ---
@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def jurados_categorias(request):
    if request.method == "POST":
        data = _body(request)
        res = call_procedure("asignarjuradocategoria", [data["IdMiembro"], data["IdCategoria"]])
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 201 if res["success"] else 400)
    if request.method == "DELETE":
        id_miembro = request.GET.get("id_miembro")
        id_categoria = request.GET.get("id_categoria")
        if not id_miembro or not id_categoria:
            return _error("Faltan parámetros id_miembro e id_categoria")
        res = call_procedure("removerjuradocategoria", [id_miembro, id_categoria])
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 200 if res["success"] else 400)

# --- EVALUACIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def evaluaciones(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_evaluaciones WHERE idevaluacion = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_evaluaciones ORDER BY idevaluacion"))

    return handle_crud(
        request, "registrarevaluacion", "actualizarevaluacion", "eliminarevaluacion",
        lambda d: [d["IdMiembro"], d["IdPelicula"], d["IdCategoria"], d.get("IdEdicion"), d["Puntuacion"], d.get("Comentario")],
        lambda i, d: [i, d["IdMiembro"], d["IdPelicula"], d["IdCategoria"], d.get("IdEdicion"), d["Puntuacion"], d.get("Comentario")],
        id
    )

# --- PATROCINADORES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def patrocinadores(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_patrocinadores WHERE idpatrocinador = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_patrocinadores ORDER BY nombreempresa"))

    return handle_crud(
        request, "registrarpatrocinador", "actualizarpatrocinador", "eliminarpatrocinador",
        lambda d: [d["NombreEmpresa"], d.get("Contacto"), d.get("Email"), d.get("RedesSociales")],
        lambda i, d: [i, d["NombreEmpresa"], d.get("Contacto"), d.get("Email"), d.get("RedesSociales")],
        id
    )

# --- PATROCINIOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def patrocinios(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_patrocinios WHERE idpatrocinio = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_patrocinios ORDER BY anio DESC"))

    return handle_crud(
        request, "registrarpatrocinio", "actualizarpatrocinio", "eliminarpatrocinio",
        lambda d: [d["IdPatrocinador"], d["IdEdicion"], d["TipoAporte"], d.get("Monto"), d.get("DescripcionAporte")],
        lambda i, d: [i, d["IdPatrocinador"], d["IdEdicion"], d["TipoAporte"], d.get("Monto"), d.get("DescripcionAporte")],
        id
    )

# --- EDICIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def ediciones(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_ediciones WHERE idedicion = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_ediciones ORDER BY anio DESC"))

    return handle_crud(
        request, "registraredicion", "actualizaredicion", "eliminaredicion",
        lambda d: [d["Anio"], d["NombreEdicion"], d["FechaInicio"], d["FechaFin"]],
        lambda i, d: [i, d["Anio"], d["NombreEdicion"], d["FechaInicio"], d["FechaFin"]],
        id
    )

# --- HOTELES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def hoteles(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_hoteles WHERE idhotel = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_hoteles ORDER BY nombrehotel"))

    return handle_crud(
        request, "registrarhotel", "actualizarhotel", "eliminarhotel",
        lambda d: [d["NombreHotel"], d.get("Direccion"), d.get("Estrellas")],
        lambda i, d: [i, d["NombreHotel"], d.get("Direccion"), d.get("Estrellas")],
        id
    )

# --- ALOJAMIENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def alojamientos(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_alojamientos WHERE idalojamiento = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_alojamientos ORDER BY checkin"))

    return handle_crud(
        request, "registraralojamiento", "actualizaralojamiento", "eliminaralojamiento",
        lambda d: [d["IdPersonal"], d["IdHotel"], d.get("IdEdicion"), d["NroHabitacion"], d["CheckIn"], d["CheckOut"]],
        lambda i, d: [i, d["IdPersonal"], d["IdHotel"], d.get("IdEdicion"), d["NroHabitacion"], d["CheckIn"], d["CheckOut"]],
        id
    )

# --- TRASLADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def traslados(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_traslados WHERE idtraslado = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_traslados ORDER BY fechahora"))

    return handle_crud(
        request, "registrartraslado", "actualizartraslado", "eliminartraslado",
        lambda d: [d["IdPersonal"], d.get("IdEdicion"), d["TipoTraslado"], d["Origen"], d["Destino"], d["FechaHora"], d.get("NroVuelo")],
        lambda i, d: [i, d["IdPersonal"], d.get("IdEdicion"), d["TipoTraslado"], d["Origen"], d["Destino"], d["FechaHora"], d.get("NroVuelo")],
        id
    )

# --- COMPETENCIA ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def competencia(request):
    if request.method == "GET":
        return _json(query_view("SELECT * FROM vw_competencia ORDER BY nombrecategoria, titulo"))

    if request.method == "POST":
        data = _body(request)
        res = call_procedure("registrarcompetencia", [data["IdPelicula"], data["IdCategoria"], data.get("IdEdicion")])
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 201 if res["success"] else 400)
    
    if request.method == "DELETE":
        pelicula_id = request.GET.get("pelicula")
        categoria_id = request.GET.get("categoria")
        edicion_id = request.GET.get("edicion")
        res = call_procedure("eliminarcompetencia", [pelicula_id, categoria_id, edicion_id])
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 200 if res["success"] else 400)

# --- ROLES PELICULA ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def roles_pelicula(request):
    if request.method == "GET":
        personal_id = request.GET.get("personal")
        pelicula_id = request.GET.get("pelicula")
        if personal_id:
            return _json(query_view("SELECT * FROM vw_rolespelicula WHERE idpersonal = %s", [personal_id]))
        if pelicula_id:
            return _json(query_view("SELECT * FROM vw_rolespelicula WHERE idpelicula = %s", [pelicula_id]))
        return _json(query_view("SELECT * FROM vw_rolespelicula"))

    if request.method == "POST":
        data = _body(request)
        res = call_procedure("registrarrol", [data["IdPersonal"], data["IdPelicula"], data["Rol"]])
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 201 if res["success"] else 400)
    
    if request.method == "DELETE":
        personal_id = request.GET.get("personal")
        pelicula_id = request.GET.get("pelicula")
        rol = request.GET.get("rol")
        res = call_procedure("eliminarrol", [personal_id, pelicula_id, rol])
        return _json({"message": res["message"]} if res["success"] else {"error": res["error"]}, 200 if res["success"] else 400)

# --- PREMIOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def premios(request, id=None):
    if request.method == "GET":
        if id:
            rows = query_view("SELECT * FROM vw_premios WHERE idpremio = %s", [id])
            return _json(rows[0]) if rows else _not_found()
        return _json(query_view("SELECT * FROM vw_premios ORDER BY anio DESC, nombrecategoria"))

    return handle_crud(
        request, "registrarpremio", "actualizarpremio", "eliminarpremio",
        lambda d: [d["IdCategoria"], d["IdPelicula"], d.get("IdEdicion")],
        lambda i, d: [i, d["IdCategoria"], d["IdPelicula"], d.get("IdEdicion")],
        id
    )

# --- TIPOS DE ABONO / TARIFAS ---
@csrf_exempt
@require_http_methods(["GET"])
def tipos_abono(request):
    return _json(query_view("SELECT * FROM vw_tiposabono ORDER BY precio DESC"))

@csrf_exempt
@require_http_methods(["GET"])
def tarifas(request):
    return _json(query_view("SELECT * FROM vw_tarifas ORDER BY precio DESC"))

# --- REPORTES ---
@csrf_exempt
def reporte_ranking(request):
    id_edicion = request.GET.get("id_edicion")
    res = call_procedure("fn_call_reporteranking", [id_edicion] if id_edicion else [None])
    # fn_call_reporteranking solo retorna texto, pero la vista esperaba filas? No, el frontend lo agarra como lista o texto. 
    # Wait, the frontend might just display the message if it's text. Let's return as a list with the message.
    return _json([{"Respuesta": res["message"]}])

@csrf_exempt
def reporte_premiacion(request):
    id_edicion = request.GET.get("id_edicion")
    res = call_procedure("fn_call_reportepremiacion", [id_edicion] if id_edicion else [None])
    return _json([{"Respuesta": res["message"]}])

@csrf_exempt
def reporte_financiero(request):
    id_edicion = request.GET.get("id_edicion")
    res = call_procedure("fn_call_reporterinanciero", [id_edicion] if id_edicion else [None])
    return _json([{"Respuesta": res["message"]}])

@csrf_exempt
def reporte_ocupacion_salas(request):
    id_edicion = request.GET.get("id_edicion")
    res = call_procedure("fn_reporte_ocupacion", [id_edicion] if id_edicion else [None])
    return _json([{"Respuesta": res["message"]}])

@csrf_exempt
def reporte_ventas_edicion(request, id):
    # Depending on how it's implemented. We just return a message for now.
    return _json([{"Respuesta": "Reporte generado"}])
