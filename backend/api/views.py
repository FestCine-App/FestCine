import json
import random
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction, connection
from django.utils import timezone
from django.db.models import Count, Sum, F, FloatField, Value, Case, When, Subquery, OuterRef, Avg, DecimalField, CharField, Q
from django.db.models.functions import Coalesce
from . import models


def _json(data, status=200):
    return JsonResponse(data, safe=False, status=status)


def _body(request):
    return json.loads(request.body) if request.body else {}


def _not_found(msg="No encontrado"):
    return _json({"error": msg}, 404)


def _error(msg, status=400):
    return _json({"error": msg}, status)


def _db_error(e):
    msg = str(e)
    if "unique" in msg.lower() or "duplicate" in msg.lower():
        return _json({"error": "Ya existe un registro igual (restricción de unicidad). Verifique los datos."}, 409)
    if "foreign key" in msg.lower() or "violates" in msg.lower():
        return _json({"error": "Error de integridad: referencia inválida en la base de datos."}, 400)
    if "not null" in msg.lower():
        return _json({"error": "Faltan datos obligatorios."}, 400)
    return _json({"error": f"Error de base de datos: {msg}"}, 500)


def _current_edicion_id():
    r = models.Edicion.objects.values('IdEdicion').order_by('-Anio').first()
    return r["IdEdicion"] if r else None


def _rows(qs):
    """Convierte un QuerySet.values() en lista de dicts."""
    return list(qs)


def _row(qs):
    """Primer elemento de un QuerySet.values() o None."""
    return qs.first()





# --- PELICULAS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def peliculas(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.Pelicula.objects.filter(IdPelicula=id).values())
            if not r:
                return _not_found()
            pgs = list(models.PeliculaGenero.objects.filter(IdPelicula=id).values('IdGenero'))
            gnrs = {g['IdGenero']: g['NombreGenero'] for g in models.Genero.objects.values('IdGenero', 'NombreGenero')}
            r['Generos'] = ', '.join(gnrs.get(pg['IdGenero'], '') for pg in pgs)
            return _json(r)
        peliculas = list(models.Pelicula.objects.values().order_by('Titulo'))
        pgs = list(models.PeliculaGenero.objects.values('IdPelicula', 'IdGenero'))
        gnrs = {g['IdGenero']: g['NombreGenero'] for g in models.Genero.objects.values('IdGenero', 'NombreGenero')}
        pg_map = {}
        for pg in pgs:
            pg_map.setdefault(pg['IdPelicula'], []).append(gnrs.get(pg['IdGenero'], ''))
        for p in peliculas:
            p['Generos'] = ', '.join(pg_map.get(p['IdPelicula'], []))
        return _json(peliculas)

    if request.method == "POST":
        data = _body(request)
        obj = models.Pelicula.objects.create(
            Titulo=data["Titulo"],
            AnioProd=data["AnioProd"],
            Duracion=data["Duracion"],
            PaisOrigen=data["PaisOrigen"],
            Sinopsis=data.get("Sinopsis"),
            Clasificacion=data["Clasificacion"],
            Formato=data["Formato"],
            Estado=data.get("Estado", "Postulada"),
        )
        pid = obj.IdPelicula
        for g in data.get("generos", []):
            models.PeliculaGenero.objects.create(IdPelicula=pid, IdGenero=g)
        id_edicion = data.get("IdEdicion")
        for c in data.get("categorias", []):
            models.CompetenciaPelicula.objects.get_or_create(
                IdPelicula=pid, IdCategoria=c, IdEdicion=id_edicion
            )
        return _json({"id": pid}, 201)

    if request.method == "PUT":
        data = _body(request)
        models.Pelicula.objects.filter(IdPelicula=id).update(
            Titulo=data["Titulo"],
            AnioProd=data["AnioProd"],
            Duracion=data["Duracion"],
            PaisOrigen=data["PaisOrigen"],
            Sinopsis=data.get("Sinopsis"),
            Clasificacion=data["Clasificacion"],
            Formato=data["Formato"],
            Estado=data["Estado"],
        )
        if "generos" in data:
            models.PeliculaGenero.objects.filter(IdPelicula=id).delete()
            for g in data["generos"]:
                models.PeliculaGenero.objects.create(IdPelicula=id, IdGenero=g)
        if data.get("IdEdicion") and "categorias" in data:
            models.CompetenciaPelicula.objects.filter(
                IdPelicula=id, IdEdicion=data["IdEdicion"]
            ).delete()
            for c in data["categorias"]:
                models.CompetenciaPelicula.objects.create(
                    IdPelicula=id, IdCategoria=c, IdEdicion=data["IdEdicion"]
                )
        return _json({"message": "Actualizada"})

    if request.method == "DELETE":
        proyecciones = models.Proyeccion.objects.filter(IdPelicula=id).values_list('IdProyeccion', flat=True)
        models.Entrada.objects.filter(IdProyeccion__in=proyecciones).delete()
        models.Proyeccion.objects.filter(IdPelicula=id).delete()
        models.CompetenciaPelicula.objects.filter(IdPelicula=id).delete()
        models.Evaluacion.objects.filter(IdPelicula=id).delete()
        models.Premio.objects.filter(IdPelicula=id).delete()
        models.RolesPelicula.objects.filter(IdPelicula=id).delete()
        models.PeliculaGenero.objects.filter(IdPelicula=id).delete()
        models.Pelicula.objects.filter(IdPelicula=id).delete()
        return _json({"message": "Eliminada"})


# --- PROYECCIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def proyecciones(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwProyeccion.objects.filter(IdProyeccion=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwProyeccion.objects.values().order_by('FechaHora')))

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            sala = models.Sala.objects.get(IdSala=data["IdSala"])
            proyeccion = models.Proyeccion.objects.create(
                IdPelicula_id=data["IdPelicula"],
                IdSala_id=data["IdSala"],
                IdEdicion_id=id_edicion,
                FechaHora=data["FechaHora"],
                TieneQA=data.get("TieneQA", False),
                AforoDisponible=sala.Capacidad,
            )
            return _json({"message": f"Proyeccion programada. ID: {proyeccion.IdProyeccion}"}, 201)
        except models.Sala.DoesNotExist:
            return _error("La sala indicada no existe.", 404)
        except Exception as e:
            msg = str(e)
            if "Control de Agenda" in msg:
                return _error(msg.split("\n")[0], 409)
            return _error(msg.split("\n")[0], 409)

    if request.method == "DELETE":
        models.Entrada.objects.filter(IdProyeccion=id).delete()
        models.Proyeccion.objects.filter(IdProyeccion=id).delete()
        return _json({"message": "Eliminada"})


# --- ASISTENTES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def asistentes(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwAsistente.objects.filter(IdAsistente=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwAsistente.objects.values().order_by('Nombre')))

    if request.method == "POST":
        data = _body(request)
        obj = models.Asistente.objects.create(
            Nombre=data["Nombre"],
            Email=data["Email"],
            Telefono=data.get("Telefono"),
            TipoAsistente=data.get("TipoAsistente", "General"),
        )
        return _json({"id": obj.IdAsistente}, 201)


# --- ENTRADAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def entradas(request):
    if request.method == "GET":
        return _json(_rows(models.VwEntrada.objects.values().order_by('-FechaCompra')))

    if request.method == "POST":
        data = _body(request)
        try:
            if data.get("IdProyeccion"):
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT respuesta FROM fn_call_comprarentrada(%s, %s, %s)",
                        [data["IdAsistente"], data["IdProyeccion"], data["IdTarifa"]]
                    )
                    resultado = cursor.fetchone()[0]
                    if resultado.startswith("Error") or resultado.startswith("Lo sentimos"):
                        return _error(resultado)
                return _json({"message": resultado}, 201)

            elif data.get("IdEvento"):
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT respuesta FROM fn_call_comprarentradaevento(%s, %s, %s)",
                        [data["IdAsistente"], data["IdEvento"], data["IdTarifa"]]
                    )
                    resultado = cursor.fetchone()[0]
                    if resultado.startswith("Error") or resultado.startswith("Lo sentimos"):
                        return _error(resultado)
                return _json({"message": resultado}, 201)

            else:
                return _error("Debe especificar una proyeccion o un evento")

        except models.Proyeccion.DoesNotExist:
            return _error("La proyeccion indicada no existe.")
        except models.EventoParalelo.DoesNotExist:
            return _error("El evento indicado no existe.")
        except Exception as e:
            return _error(str(e).split("\n")[0])


# --- ABONOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def abonos(request):
    if request.method == "GET":
        return _json(_rows(models.VwAbono.objects.values().order_by('-FechaCompra')))

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT respuesta FROM fn_call_venderabono(%s, %s, %s, %s)",
                    [data["IdAsistente"], data["IdTipoAbono"], id_edicion, data.get("PagoExitoso", True)]
                )
                resultado = cursor.fetchone()[0]
                if resultado.startswith("Error") or resultado.startswith("Lo sentimos") or resultado.startswith("Pasarela"):
                    return _error(resultado)
            return _json({"message": resultado}, 201)
        except Exception as e:
            return _error(str(e).split("\n")[0])


# --- SEDES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def sedes(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.Sede.objects.filter(IdSede=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.Sede.objects.values().order_by('NombreSede')))

    if request.method == "POST":
        data = _body(request)
        obj = models.Sede.objects.create(
            NombreSede=data["NombreSede"],
            Direccion=data.get("Direccion"),
            Ciudad=data.get("Ciudad"),
            SitioWeb=data.get("SitioWeb"),
        )
        return _json({"id": obj.IdSede}, 201)

    if request.method == "DELETE":
        models.Sala.objects.filter(IdSede=id).delete()
        models.Sede.objects.filter(IdSede=id).delete()
        return _json({"message": "Eliminada"})


# --- SALAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def salas(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwSala.objects.filter(IdSala=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwSala.objects.values().order_by('NombreSede', 'NombreSala')))

    if request.method == "POST":
        data = _body(request)
        obj = models.Sala.objects.create(
            NombreSala=data["NombreSala"],
            Capacidad=data["Capacidad"],
            IdSede_id=data["IdSede"],
        )
        return _json({"id": obj.IdSala}, 201)


# --- EVENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def eventos(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwEvento.objects.filter(IdEvento=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwEvento.objects.values().order_by('FechaHora')))

    if request.method == "POST":
        try:
            data = _body(request)
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            obj = models.EventoParalelo.objects.create(
                IdEdicion_id=id_edicion,
                NombreEvento=data["NombreEvento"],
                TipoEvento=data["TipoEvento"],
                FechaHora=data["FechaHora"],
                Aforo=data["Aforo"],
                CostoInscripcion=data.get("CostoInscripcion", 0),
            )
            eid = obj.IdEvento
            for p in data.get("expositores", []):
                models.ExpositorEvento.objects.create(IdEvento=eid, IdPersonal=p)
            return _json({"id": eid}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        models.EventoParalelo.objects.filter(IdEvento=id).update(
            NombreEvento=data["NombreEvento"],
            TipoEvento=data["TipoEvento"],
            FechaHora=data["FechaHora"],
            Aforo=data["Aforo"],
            CostoInscripcion=data.get("CostoInscripcion", 0),
        )
        if "expositores" in data:
            models.ExpositorEvento.objects.filter(IdEvento=id).delete()
            for p in data["expositores"]:
                models.ExpositorEvento.objects.create(IdEvento=id, IdPersonal=p)
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        models.Entrada.objects.filter(IdEvento=id).delete()
        models.ExpositorEvento.objects.filter(IdEvento=id).delete()
        models.EventoParalelo.objects.filter(IdEvento=id).delete()
        return _json({"message": "Eliminado"})


# --- GENEROS ---
@csrf_exempt
@require_http_methods(["GET"])
def generos(request):
    return _json(_rows(models.Genero.objects.values().order_by('NombreGenero')))


# --- PERSONAL ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def personal(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwPersonal.objects.filter(IdPersonal=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwPersonal.objects.values().order_by('Nombre')))

    if request.method == "POST":
        data = _body(request)
        obj = models.Personal.objects.create(
            Nombre=data["Nombre"],
            Biografia=data.get("Biografia"),
            Email=data.get("Email"),
            Telefono=data.get("Telefono"),
            Nacionalidad=data.get("Nacionalidad"),
        )
        return _json({"id": obj.IdPersonal}, 201)

    if request.method == "PUT":
        data = _body(request)
        models.Personal.objects.filter(IdPersonal=id).update(
            Nombre=data["Nombre"],
            Biografia=data.get("Biografia"),
            Email=data.get("Email"),
            Telefono=data.get("Telefono"),
            Nacionalidad=data.get("Nacionalidad"),
        )
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        models.RolesPelicula.objects.filter(IdPersonal=id).delete()
        models.ExpositorEvento.objects.filter(IdPersonal=id).delete()
        models.Alojamiento.objects.filter(IdPersonal=id).delete()
        models.Traslado.objects.filter(IdPersonal=id).delete()
        models.Personal.objects.filter(IdPersonal=id).delete()
        return _json({"message": "Eliminado"})


# --- CATEGORIAS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def categorias(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.Categoria.objects.filter(IdCategoria=id).values())
            return _json(r) if r else _not_found()
        jurado_id = request.GET.get('jurado')
        categoria_id = request.GET.get('categoria')
        if jurado_id:
            return _json(_rows(
                models.VwCategoriasPorJurado.objects.filter(IdMiembro=jurado_id)
                .values().order_by('NombreCategoria')
            ))
        if categoria_id:
            id_edicion = request.GET.get("id_edicion")
            pelicula_ids = models.CompetenciaPelicula.objects.filter(
                IdCategoria=categoria_id
            )
            if id_edicion:
                pelicula_ids = pelicula_ids.filter(IdEdicion=id_edicion)
            return _json(_rows(
                models.Pelicula.objects.filter(
                    IdPelicula__in=pelicula_ids.values('IdPelicula')
                ).values('IdPelicula', 'Titulo').order_by('Titulo')
            ))
        return _json(_rows(models.Categoria.objects.values().order_by('NombreCategoria')))

    if request.method == "POST":
        data = _body(request)
        obj = models.Categoria.objects.create(
            NombreCategoria=data["NombreCategoria"],
            Descripcion=data.get("Descripcion"),
        )
        return _json({"id": obj.IdCategoria}, 201)

    if request.method == "PUT":
        data = _body(request)
        models.Categoria.objects.filter(IdCategoria=id).update(
            NombreCategoria=data["NombreCategoria"],
            Descripcion=data.get("Descripcion"),
        )
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        models.CompetenciaPelicula.objects.filter(IdCategoria=id).delete()
        models.JuradoCategoria.objects.filter(IdCategoria=id).delete()
        models.Evaluacion.objects.filter(IdCategoria=id).delete()
        models.Premio.objects.filter(IdCategoria=id).delete()
        models.Categoria.objects.filter(IdCategoria=id).delete()
        return _json({"message": "Eliminado"})


# --- JURADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def jurados(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.MiembroJurado.objects.filter(IdMiembro=id).select_related('IdEdicion').values('IdMiembro', 'Nombre', 'Profesion', 'Pais', 'Email', 'IdEdicion_id', EdicionNombre=F('IdEdicion__NombreEdicion')))
            if not r:
                return _not_found()
            r['IdEdicion'] = r.pop('IdEdicion_id')
            return _json(r)
        rows = _rows(models.MiembroJurado.objects.select_related('IdEdicion').values('IdMiembro', 'Nombre', 'Profesion', 'Pais', 'Email', 'IdEdicion_id', EdicionNombre=F('IdEdicion__NombreEdicion')).order_by('Nombre'))
        for r in rows:
            r['IdEdicion'] = r.pop('IdEdicion_id')
        return _json(rows)

    if request.method == "POST":
        data = _body(request)
        obj = models.MiembroJurado.objects.create(
            Nombre=data["Nombre"],
            Profesion=data.get("Profesion"),
            Pais=data.get("Pais"),
            Email=data.get("Email"),
            IdEdicion_id=data.get("IdEdicion") or _current_edicion_id(),
        )
        return _json({"id": obj.IdMiembro}, 201)

    if request.method == "PUT":
        data = _body(request)
        vals = {
            "Nombre": data["Nombre"],
            "Profesion": data.get("Profesion"),
            "Pais": data.get("Pais"),
            "Email": data.get("Email"),
        }
        if data.get("IdEdicion"):
            vals["IdEdicion_id"] = data["IdEdicion"]
        models.MiembroJurado.objects.filter(IdMiembro=id).update(**vals)
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        models.JuradoCategoria.objects.filter(IdMiembro=id).delete()
        models.Evaluacion.objects.filter(IdMiembro=id).delete()
        models.MiembroJurado.objects.filter(IdMiembro=id).delete()
        return _json({"message": "Eliminado"})


# --- JURADO ASIGNACIONES ---
@csrf_exempt
@require_http_methods(["GET"])
def jurados_asignaciones(request):
    id_jurado = request.GET.get("id_jurado")
    id_edicion = request.GET.get("id_edicion")
    if not id_jurado or not id_edicion:
        return _error("Faltan parámetros id_jurado e id_edicion")
    cat_ids = list(models.JuradoCategoria.objects.filter(
        IdMiembro=id_jurado
    ).values_list('IdCategoria', flat=True))
    rows = list(models.VwCompetencia.objects.filter(
        IdCategoria__in=cat_ids, IdEdicion=id_edicion
    ).values('IdPelicula', 'Titulo', 'IdCategoria', 'NombreCategoria').order_by('NombreCategoria', 'Titulo'))
    result = []
    for r in rows:
        eval_row = models.Evaluacion.objects.filter(
            IdMiembro=id_jurado, IdPelicula=r['IdPelicula'],
            IdCategoria=r['IdCategoria'], IdEdicion=id_edicion
        ).values('IdEvaluacion', 'Puntuacion').first()
        result.append({
            'IdPelicula': r['IdPelicula'], 'Titulo': r['Titulo'],
            'IdCategoria': r['IdCategoria'], 'NombreCategoria': r['NombreCategoria'],
            'Evaluada': eval_row is not None,
            'Puntuacion': eval_row['Puntuacion'] if eval_row else None,
            'IdEvaluacion': eval_row['IdEvaluacion'] if eval_row else None,
        })
    return _json(result)


# --- JURADO CATEGORIAS ---
@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def jurados_categorias(request):
    if request.method == "POST":
        data = _body(request)
        try:
            models.JuradoCategoria.objects.create(
                IdMiembro=data["IdMiembro"], IdCategoria=data["IdCategoria"]
            )
            return _json({"message": "Categoría asignada al jurado"}, 201)
        except Exception as e:
            return _db_error(e)
    if request.method == "DELETE":
        id_miembro = request.GET.get("id_miembro")
        id_categoria = request.GET.get("id_categoria")
        if not id_miembro or not id_categoria:
            return _error("Faltan parámetros id_miembro e id_categoria")
        models.JuradoCategoria.objects.filter(
            IdMiembro=id_miembro, IdCategoria=id_categoria
        ).delete()
        return _json({"message": "Categoría removida del jurado"})


# --- EVALUACIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def evaluaciones(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwEvaluacion.objects.filter(IdEvaluacion=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwEvaluacion.objects.values().order_by('IdEvaluacion')))

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            obj = models.Evaluacion.objects.create(
                IdMiembro=data["IdMiembro"],
                IdPelicula=data["IdPelicula"],
                IdCategoria=data["IdCategoria"],
                IdEdicion=id_edicion,
                Puntuacion=data["Puntuacion"],
                Comentario=data.get("Comentario"),
            )
            return _json({"id": obj.IdEvaluacion}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            models.Evaluacion.objects.filter(IdEvaluacion=id).update(
                IdMiembro=data["IdMiembro"],
                IdPelicula=data["IdPelicula"],
                IdCategoria=data["IdCategoria"],
                IdEdicion=id_edicion,
                Puntuacion=data["Puntuacion"],
                Comentario=data.get("Comentario"),
            )
            return _json({"message": "Actualizado"})
        except Exception as e:
            return _db_error(e)

    if request.method == "DELETE":
        models.Evaluacion.objects.filter(IdEvaluacion=id).delete()
        return _json({"message": "Eliminado"})


# --- PATROCINADORES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def patrocinadores(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.Patrocinador.objects.filter(IdPatrocinador=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.Patrocinador.objects.values().order_by('NombreEmpresa')))

    if request.method == "POST":
        data = _body(request)
        obj = models.Patrocinador.objects.create(
            NombreEmpresa=data["NombreEmpresa"],
            Contacto=data.get("Contacto"),
            Email=data.get("Email"),
            RedesSociales=data.get("RedesSociales"),
        )
        return _json({"id": obj.IdPatrocinador}, 201)

    if request.method == "PUT":
        data = _body(request)
        models.Patrocinador.objects.filter(IdPatrocinador=id).update(
            NombreEmpresa=data["NombreEmpresa"],
            Contacto=data.get("Contacto"),
            Email=data.get("Email"),
            RedesSociales=data.get("RedesSociales"),
        )
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        models.PatrocinioEdicion.objects.filter(IdPatrocinador=id).delete()
        models.Patrocinador.objects.filter(IdPatrocinador=id).delete()
        return _json({"message": "Eliminado"})


# --- PATROCINIOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def patrocinios(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwPatrocinio.objects.filter(IdPatrocinio=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwPatrocinio.objects.values().order_by('-Anio')))

    if request.method == "POST":
        data = _body(request)
        obj = models.PatrocinioEdicion.objects.create(
            IdPatrocinador=data["IdPatrocinador"],
            IdEdicion=data["IdEdicion"],
            TipoAporte=data["TipoAporte"],
            Monto=data.get("Monto"),
            DescripcionAporte=data.get("DescripcionAporte"),
        )
        return _json({"id": obj.IdPatrocinio}, 201)

    if request.method == "PUT":
        data = _body(request)
        models.PatrocinioEdicion.objects.filter(IdPatrocinio=id).update(
            IdPatrocinador=data["IdPatrocinador"],
            IdEdicion=data["IdEdicion"],
            TipoAporte=data["TipoAporte"],
            Monto=data.get("Monto"),
            DescripcionAporte=data.get("DescripcionAporte"),
        )
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        models.PatrocinioEdicion.objects.filter(IdPatrocinio=id).delete()
        return _json({"message": "Eliminado"})


# --- EDICIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def ediciones(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.Edicion.objects.filter(IdEdicion=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.Edicion.objects.values().order_by('-Anio')))

    if request.method == "POST":
        data = _body(request)
        obj = models.Edicion.objects.create(
            Anio=data["Anio"],
            NombreEdicion=data["NombreEdicion"],
            FechaInicio=data["FechaInicio"],
            FechaFin=data["FechaFin"],
        )
        return _json({"id": obj.IdEdicion}, 201)

    if request.method == "PUT":
        data = _body(request)
        models.Edicion.objects.filter(IdEdicion=id).update(
            Anio=data["Anio"],
            NombreEdicion=data["NombreEdicion"],
            FechaInicio=data["FechaInicio"],
            FechaFin=data["FechaFin"],
        )
        return _json({"message": "Actualizada"})

    if request.method == "DELETE":
        with transaction.atomic():
            jurados_ids = models.MiembroJurado.objects.filter(IdEdicion_id=id).values('IdMiembro')
            proy_ids = models.Proyeccion.objects.filter(IdEdicion_id=id).values('IdProyeccion')
            evt_ids = models.EventoParalelo.objects.filter(IdEdicion_id=id).values('IdEvento')

            models.Entrada.objects.filter(IdProyeccion__in=proy_ids).delete()
            models.Entrada.objects.filter(IdEvento__in=evt_ids).delete()
            models.ExpositorEvento.objects.filter(IdEvento__in=evt_ids).delete()
            models.Evaluacion.objects.filter(IdEdicion=id).delete()
            models.JuradoCategoria.objects.filter(IdMiembro__in=jurados_ids).delete()
            models.Proyeccion.objects.filter(IdEdicion_id=id).delete()
            models.EventoParalelo.objects.filter(IdEdicion_id=id).delete()
            models.MiembroJurado.objects.filter(IdEdicion_id=id).delete()
            models.CompetenciaPelicula.objects.filter(IdEdicion=id).delete()
            models.Premio.objects.filter(IdEdicion_id=id).delete()
            models.Abono.objects.filter(IdEdicion_id=id).delete()
            models.Alojamiento.objects.filter(IdEdicion=id).delete()
            models.Traslado.objects.filter(IdEdicion=id).delete()
            models.PatrocinioEdicion.objects.filter(IdEdicion=id).delete()
            models.Edicion.objects.filter(IdEdicion=id).delete()
        return _json({"message": "Eliminada"})


# --- HOTELES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def hoteles(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.Hotel.objects.filter(IdHotel=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.Hotel.objects.values().order_by('NombreHotel')))

    if request.method == "POST":
        data = _body(request)
        obj = models.Hotel.objects.create(
            NombreHotel=data["NombreHotel"],
            Direccion=data.get("Direccion"),
            Estrellas=data.get("Estrellas"),
        )
        return _json({"id": obj.IdHotel}, 201)

    if request.method == "PUT":
        data = _body(request)
        models.Hotel.objects.filter(IdHotel=id).update(
            NombreHotel=data["NombreHotel"],
            Direccion=data.get("Direccion"),
            Estrellas=data.get("Estrellas"),
        )
        return _json({"message": "Actualizado"})

    if request.method == "DELETE":
        models.Alojamiento.objects.filter(IdHotel=id).delete()
        models.Hotel.objects.filter(IdHotel=id).delete()
        return _json({"message": "Eliminado"})


# --- ALOJAMIENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def alojamientos(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwAlojamiento.objects.filter(IdAlojamiento=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwAlojamiento.objects.values().order_by('CheckIn')))

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            obj = models.Alojamiento.objects.create(
                IdPersonal=data["IdPersonal"],
                IdHotel=data["IdHotel"],
                IdEdicion=id_edicion,
                NroHabitacion=data["NroHabitacion"],
                CheckIn=data["CheckIn"],
                CheckOut=data["CheckOut"],
            )
            return _json({"id": obj.IdAlojamiento}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            models.Alojamiento.objects.filter(IdAlojamiento=id).update(
                IdPersonal=data["IdPersonal"],
                IdHotel=data["IdHotel"],
                IdEdicion=id_edicion,
                NroHabitacion=data["NroHabitacion"],
                CheckIn=data["CheckIn"],
                CheckOut=data["CheckOut"],
            )
            return _json({"message": "Actualizado"})
        except Exception as e:
            return _db_error(e)

    if request.method == "DELETE":
        models.Alojamiento.objects.filter(IdAlojamiento=id).delete()
        return _json({"message": "Eliminado"})


# --- TRASLADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def traslados(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwTraslado.objects.filter(IdTraslado=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwTraslado.objects.values().order_by('FechaHora')))

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            obj = models.Traslado.objects.create(
                IdPersonal=data["IdPersonal"],
                IdEdicion=id_edicion,
                TipoTraslado=data["TipoTraslado"],
                Origen=data["Origen"],
                Destino=data["Destino"],
                FechaHora=data["FechaHora"],
                NroVuelo=data.get("NroVuelo"),
            )
            return _json({"id": obj.IdTraslado}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            models.Traslado.objects.filter(IdTraslado=id).update(
                IdPersonal=data["IdPersonal"],
                IdEdicion=id_edicion,
                TipoTraslado=data["TipoTraslado"],
                Origen=data["Origen"],
                Destino=data["Destino"],
                FechaHora=data["FechaHora"],
                NroVuelo=data.get("NroVuelo"),
            )
            return _json({"message": "Actualizado"})
        except Exception as e:
            return _db_error(e)

    if request.method == "DELETE":
        models.Traslado.objects.filter(IdTraslado=id).delete()
        return _json({"message": "Eliminado"})


# --- PREMIOS ---
@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def premios(request, id=None):
    if request.method == "GET":
        if id:
            r = _row(models.VwPremio.objects.filter(IdPremio=id).values())
            return _json(r) if r else _not_found()
        return _json(_rows(models.VwPremio.objects.values().order_by('-Anio', 'NombreCategoria')))

    if request.method == "POST":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            obj = models.Premio.objects.create(
                IdCategoria_id=data["IdCategoria"],
                IdPelicula_id=data["IdPelicula"],
                IdEdicion_id=id_edicion,
            )
            return _json({"id": obj.IdPremio}, 201)
        except Exception as e:
            return _db_error(e)

    if request.method == "PUT":
        data = _body(request)
        try:
            id_edicion = data.get("IdEdicion") or _current_edicion_id()
            models.Premio.objects.filter(IdPremio=id).update(
                IdCategoria=data["IdCategoria"],
                IdPelicula=data["IdPelicula"],
                IdEdicion=id_edicion,
            )
            return _json({"message": "Actualizado"})
        except Exception as e:
            return _db_error(e)

    if request.method == "DELETE":
        models.Premio.objects.filter(IdPremio=id).delete()
        return _json({"message": "Eliminado"})


# --- TARIFAS ---
@csrf_exempt
@require_http_methods(["GET"])
def tarifas(request):
    return _json(_rows(models.VwTarifa.objects.values()))


# --- TIPOS ABONO ---
@csrf_exempt
@require_http_methods(["GET"])
def tiposabono(request):
    return _json(_rows(models.VwTipoAbono.objects.values()))


# --- COMPETENCIA PELICULA ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def competencia(request):
    if request.method == "GET":
        pelicula_id = request.GET.get("pelicula")
        categoria_id = request.GET.get("categoria")
        qs = models.VwCompetencia.objects.values()
        if pelicula_id and categoria_id:
            r = _row(qs.filter(IdPelicula=pelicula_id, IdCategoria=categoria_id))
            return _json(r) if r else _not_found()
        if pelicula_id:
            return _json(_rows(qs.filter(IdPelicula=pelicula_id).order_by('NombreCategoria')))
        if categoria_id:
            return _json(_rows(qs.filter(IdCategoria=categoria_id).order_by('Titulo')))
        return _json(_rows(qs.order_by('Titulo', 'NombreCategoria')))

    if request.method == "POST":
        data = _body(request)
        id_edicion = data.get("IdEdicion") or _current_edicion_id()
        obj = models.CompetenciaPelicula.objects.create(
            IdPelicula=data["IdPelicula"],
            IdCategoria=data["IdCategoria"],
            IdEdicion=id_edicion,
        )
        return _json({"id": obj.IdPelicula}, 201)

    if request.method == "DELETE":
        pelicula_id = request.GET.get("pelicula")
        categoria_id = request.GET.get("categoria")
        models.CompetenciaPelicula.objects.filter(
            IdPelicula=pelicula_id, IdCategoria=categoria_id
        ).delete()
        return _json({"message": "Eliminada de competencia"})


# --- REPORTES ---
@csrf_exempt
@require_http_methods(["GET"])
def reporte_ranking(request):
    try:
        id_edicion = request.GET.get("id_edicion")
        cp_filter = {'IdEdicion': id_edicion} if id_edicion else {}
        qs = models.Proyeccion.objects.all()
        if id_edicion:
            qs = qs.filter(IdEdicion=id_edicion)
        capacidad_sub = models.Proyeccion.objects.filter(
            IdPelicula=OuterRef('IdPelicula'),
            **cp_filter,
        ).values('IdPelicula').annotate(
            cap_total=Sum('IdSala__Capacidad')
        ).values('cap_total')[:1]
        rows = list(
            qs
            .values('IdPelicula', 'IdPelicula__Titulo')
            .annotate(
                Asistentes=Count('entradas__IdEntrada', distinct=True),
                CapacidadTotal=Coalesce(Subquery(capacidad_sub), Value(0)),
            )
            .annotate(
                PctOcupacion=Case(
                    When(CapacidadTotal=0, then=Value(0.0)),
                    default=Value(100.0) * F('Asistentes') / F('CapacidadTotal'),
                    output_field=FloatField()
                ),
            )
            .order_by('-Asistentes')
        )
        for r in rows:
            r['Titulo'] = r.pop('IdPelicula__Titulo')
            r.pop('IdPelicula', None)
        return _json(rows)
    except Exception as e:
        return _db_error(e)


@csrf_exempt
@require_http_methods(["GET"])
def reporte_premiacion(request):
    id_edicion = request.GET.get("id_edicion")
    try:
        qs = models.Premio.objects.all()
        if id_edicion:
            qs = qs.filter(IdEdicion=id_edicion)
        rows = list(
            qs.annotate(
                NombreCategoria=F('IdCategoria__NombreCategoria'),
                PeliculaGanadora=F('IdPelicula__Titulo'),
                Anio=F('IdEdicion__Anio'),
            )
            .annotate(
                PromedioJurado=Subquery(
                    models.Evaluacion.objects.filter(
                        IdPelicula=OuterRef('IdPelicula'),
                        IdCategoria=OuterRef('IdCategoria'),
                        IdEdicion=OuterRef('IdEdicion'),
                    ).values('IdPelicula').annotate(
                        avg=Avg('Puntuacion')
                    ).values('avg')[:1]
                )
            )
            .values('NombreCategoria', 'PeliculaGanadora', 'PromedioJurado', 'Anio')
            .order_by('NombreCategoria')
        )
        return _json(rows)
    except Exception as e:
        return _db_error(e)


@csrf_exempt
@require_http_methods(["GET"])
def reporte_financiero(request):
    try:
        id_edicion = request.GET.get("id_edicion")
        ent_qs = models.Entrada.objects.all()
        abo_qs = models.Abono.objects.filter(Pagado=True)
        if id_edicion:
            ent_qs = ent_qs.filter(
                Q(IdProyeccion__IdEdicion=id_edicion) |
                Q(IdEvento__isnull=False, IdEvento__in=models.EventoParalelo.objects.filter(IdEdicion=id_edicion).values('IdEvento'))
            )
            abo_qs = abo_qs.filter(IdEdicion=id_edicion)
        entradas = list(
            ent_qs
            .values('IdTarifa__NombreTarifa')
            .annotate(
                TipoVenta=Value('Entrada Individual', output_field=CharField()),
                Cantidad=Count('IdEntrada'),
                Subtotal=Coalesce(Sum('IdTarifa__Precio'), Value(0, output_field=DecimalField())),
            )
            .order_by('-Subtotal')
        )
        abonos = list(
            abo_qs
            .values('IdTipoAbono__NombreAbono')
            .annotate(
                TipoVenta=Value('Abono', output_field=CharField()),
                Cantidad=Count('IdAbono'),
                Subtotal=Coalesce(Sum('IdTipoAbono__Precio'), Value(0, output_field=DecimalField())),
            )
            .order_by('-Subtotal')
        )
        for r in entradas:
            r['Categoria'] = r.pop('IdTarifa__NombreTarifa')
        for r in abonos:
            r['Categoria'] = r.pop('IdTipoAbono__NombreAbono')
        data = entradas + abonos
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
        id_edicion = request.GET.get("id_edicion")
        qs = models.Sala.objects.all()
        if id_edicion:
            qs = qs.filter(proyecciones_sala__IdEdicion=id_edicion)
        rows = list(
            qs
            .values('NombreSala', 'IdSede__NombreSede', 'Capacidad')
            .annotate(
                EntradasVendidas=Count('proyecciones_sala__entradas__IdEntrada', distinct=True),
            )
            .annotate(
                PorcentajeOcupacion=Case(
                    When(Capacidad=0, then=Value(0.0)),
                    default=Value(100.0) * F('EntradasVendidas') / F('Capacidad'),
                    output_field=FloatField()
                ),
            )
            .order_by('-PorcentajeOcupacion')
        )
        for r in rows:
            r['NombreSede'] = r.pop('IdSede__NombreSede')
        return _json(rows)
    except Exception as e:
        return _db_error(e)


@csrf_exempt
@require_http_methods(["GET"])
def reporte_ventas_edicion(request, id):
    try:
        ent = models.Entrada.objects.aggregate(
            Cantidad=Count('IdEntrada'),
            Total=Coalesce(Sum('IdTarifa__Precio'), Value(0, output_field=DecimalField())),
        )
        abo = models.Abono.objects.filter(Pagado=True).aggregate(
            Cantidad=Count('IdAbono'),
            Total=Coalesce(Sum('IdTipoAbono__Precio'), Value(0, output_field=DecimalField())),
        )
        return _json({
            "entradas": ent,
            "abonos": abo,
        })
    except Exception as e:
        return _db_error(e)


# --- ROLES PELICULA ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def roles_pelicula(request):
    if request.method == "GET":
        personal_id = request.GET.get("personal")
        pelicula_id = request.GET.get("pelicula")
        qs = models.VwRolesPelicula.objects.values()
        if personal_id:
            return _json(_rows(qs.filter(IdPersonal=personal_id)))
        if pelicula_id:
            return _json(_rows(qs.filter(IdPelicula=pelicula_id)))
        return _json(_rows(qs.order_by('Pelicula', 'Personal')))

    if request.method == "POST":
        data = _body(request)
        models.RolesPelicula.objects.create(
            IdPersonal=data["IdPersonal"],
            IdPelicula=data["IdPelicula"],
            Rol=data["Rol"],
        )
        return _json({"message": "Rol registrado"}, 201)

    if request.method == "DELETE":
        personal_id = request.GET.get("personal")
        pelicula_id = request.GET.get("pelicula")
        rol = request.GET.get("rol")
        models.RolesPelicula.objects.filter(
            IdPersonal=personal_id, IdPelicula=pelicula_id, Rol=rol
        ).delete()
        return _json({"message": "Rol eliminado"})
