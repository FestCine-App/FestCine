import json
import datetime
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Count, Sum, Avg, OuterRef, Subquery
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import (
    Genero, Pelicula, PeliculaGenero, Personal, RolPelicula, Edicion,
    Sede, Sala, Proyeccion, EventoParalelo, ExpositorEvento, Categoria,
    MiembroJurado, JuradoCategoria, CompetenciaPelicula, Evaluacion,
    Premio, Asistente, Tarifa, Entrada, TipoAbono, Abono, Hotel,
    Alojamiento, Traslado, Patrocinador, PatrocinioEdicion
)
from .serializers import (
    serialize_genero, serialize_pelicula, serialize_proyeccion,
    serialize_asistente, serialize_entrada, serialize_abono,
    serialize_sede, serialize_sala, serialize_evento,
    serialize_personal, serialize_categoria, serialize_jurado,
    serialize_evaluacion, serialize_patrocinador, serialize_patrocinio,
    serialize_edicion, serialize_hotel, serialize_alojamiento,
    serialize_traslado, serialize_premio, serialize_tarifa,
    serialize_tipo_abono, serialize_competencia
)


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
            r = Pelicula.objects.prefetch_related('generos').filter(
                id_pelicula=id,
                estado__in=['Seleccionada', 'Premiada']
            ).first()
            return _json(serialize_pelicula(r)) if r else _not_found()
        
        queryset = Pelicula.objects.prefetch_related('generos').filter(
            estado__in=['Seleccionada', 'Premiada']
        ).order_by('titulo')
        return _json([serialize_pelicula(p) for p in queryset])

    if request.method == "POST":
        data = _body(request)
        with transaction.atomic():
            pelicula = Pelicula.objects.create(
                titulo=data["Titulo"],
                anio_prod=data["AnioProd"],
                duracion=data["Duracion"],
                pais_orig=data["PaisOrigen"],
                sinopsis=data.get("Sinopsis"),
                clasificacion=data["Clasificacion"],
                formato=data["Formato"],
                estado=data.get("Estado", "Postulada")
            )
            if "generos" in data:
                pelicula.generos.set(data["generos"])
            return _json({"id": pelicula.id_pelicula}, 201)

    if request.method == "PUT":
        data = _body(request)
        with transaction.atomic():
            pelicula = Pelicula.objects.filter(id_pelicula=id).first()
            if not pelicula:
                return _not_found()
            
            pelicula.titulo = data["Titulo"]
            pelicula.anio_prod = data["AnioProd"]
            pelicula.duracion = data["Duracion"]
            pelicula.pais_orig = data["PaisOrigen"]
            pelicula.sinopsis = data.get("Sinopsis")
            pelicula.clasificacion = data["Clasificacion"]
            pelicula.formato = data["Formato"]
            pelicula.estado = data["Estado"]
            pelicula.save()
            
            if "generos" in data:
                pelicula.generos.set(data["generos"])
            return _json({"message": "Actualizada"})

    if request.method == "DELETE":
        with transaction.atomic():
            pelicula = Pelicula.objects.filter(id_pelicula=id).first()
            if not pelicula:
                return _not_found()
            pelicula.delete()
            return _json({"message": "Eliminada"})


# --- PROYECCIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def proyecciones(request, id=None):
    if request.method == "GET":
        if id:
            r = Proyeccion.objects.select_related(
                'pelicula', 'sala__sede', 'edicion'
            ).filter(id_proyeccion=id).first()
            return _json(serialize_proyeccion(r)) if r else _not_found()
        
        queryset = Proyeccion.objects.select_related(
            'pelicula', 'sala__sede', 'edicion'
        ).all().order_by('fecha_hora')
        return _json([serialize_proyeccion(p) for p in queryset])

    if request.method == "POST":
        data = _body(request)
        try:
            with transaction.atomic():
                sala = Sala.objects.filter(id_sala=data["IdSala"]).first()
                if not sala:
                    return _error("Error: La sala indicada no existe.", 409)

                pelicula = Pelicula.objects.filter(id_pelicula=data["IdPelicula"]).first()
                if not pelicula:
                    return _error("Error: La pelicula indicada no existe.", 409)

                edicion = Edicion.objects.filter(id_edicion=data["IdEdicion"]).first()
                if not edicion:
                    return _error("Error: La edicion indicada no existe.", 409)

                fecha_hora = parse_datetime(data["FechaHora"])
                if not fecha_hora:
                    return _error("Error: Formato de fecha invalido.", 409)

                # Control de Agenda (Trigger logic)
                duracion_nueva = pelicula.duracion
                fin_nueva = fecha_hora + datetime.timedelta(minutes=duracion_nueva + 30)

                conflicts = Proyeccion.objects.filter(
                    sala=sala,
                    fecha_hora__lt=fin_nueva
                ).select_related('pelicula')

                for pr in conflicts:
                    fin_existente = pr.fecha_hora + datetime.timedelta(minutes=pr.pelicula.duracion + 30)
                    if fecha_hora < fin_existente:
                        return _error(
                            f"Error: Control de Agenda: La sala ya esta ocupada por \"{pr.pelicula.titulo}\" en ese horario (incluidos 30 min de limpieza).",
                            409
                        )

                proy = Proyeccion.objects.create(
                    pelicula=pelicula,
                    sala=sala,
                    edicion=edicion,
                    fecha_hora=fecha_hora,
                    tiene_qa=data.get("TieneQA", False),
                    aforo_disponible=sala.capacidad
                )
                return _json({"message": f"Proyeccion programada exitosamente. ID: {proy.id_proyeccion}"}, 201)
        except Exception as e:
            return _error(str(e).split("\n")[0], 409)

    if request.method == "DELETE":
        with transaction.atomic():
            proy = Proyeccion.objects.filter(id_proyeccion=id).first()
            if not proy:
                return _not_found()
            proy.delete()
            return _json({"message": "Eliminada"})


# --- ASISTENTES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def asistentes(request, id=None):
    if request.method == "GET":
        if id:
            r = Asistente.objects.filter(id_asistente=id).first()
            return _json(serialize_asistente(r)) if r else _not_found()
        
        queryset = Asistente.objects.all().order_by('nombre')
        return _json([serialize_asistente(a) for a in queryset])

    if request.method == "POST":
        data = _body(request)
        asistente = Asistente.objects.create(
            nombre=data["Nombre"],
            email=data["Email"],
            telefono=data.get("Telefono"),
            tipo_asistente=data.get("TipoAsistente", "General")
        )
        return _json({"id": asistente.id_asistente}, 201)


# --- ENTRADAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def entradas(request):
    if request.method == "GET":
        queryset = Entrada.objects.select_related(
            'asistente', 'proyeccion__pelicula', 'tarifa'
        ).all().order_by('-fecha_compra')
        return _json([serialize_entrada(e) for e in queryset])

    if request.method == "POST":
        data = _body(request)
        try:
            with transaction.atomic():
                asistente_id = int(data["IdAsistente"])
                proyeccion_id = int(data["IdProyeccion"])
                tarifa_id = int(data["IdTarifa"])

                # Lock the projection row
                proy = Proyeccion.objects.select_for_update().filter(
                    id_proyeccion=proyeccion_id
                ).select_related('pelicula').first()
                if not proy:
                    return _error("Error: La proyeccion indicada no existe.")

                asis = Asistente.objects.filter(id_asistente=asistente_id).first()
                if not asis:
                    return _error("Error: El asistente indicado no existe.")

                tarifa = Tarifa.objects.filter(id_tarifa=tarifa_id).first()
                if not tarifa:
                    return _error("Error: La tarifa indicada no existe.")

                ya_compro = Entrada.objects.filter(asistente=asis, proyeccion=proy).exists()
                if ya_compro:
                    return _error("Error: El asistente ya tiene una entrada para esta proyeccion.")

                if proy.aforo_disponible <= 0:
                    return _error("Lo sentimos, no hay aforo disponible para esta funcion.")

                Entrada.objects.create(
                    asistente=asis,
                    proyeccion=proy,
                    tarifa=tarifa
                )

                proy.aforo_disponible -= 1
                proy.save()

                fecha_str = proy.fecha_hora.strftime('%d/%m/%Y %H:%M') if proy.fecha_hora else ""
                msg = f"Entrada registrada exitosamente para \"{proy.pelicula.titulo}\" el {fecha_str}."
                return _json({"message": msg}, 201)
        except Exception as e:
            return _error(str(e).split("\n")[0])


# --- ABONOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def abonos(request):
    if request.method == "GET":
        queryset = Abono.objects.select_related(
            'asistente', 'tipo_abono', 'edicion'
        ).all().order_by('-fecha_compra')
        return _json([serialize_abono(a) for a in queryset])

    if request.method == "POST":
        data = _body(request)
        try:
            with transaction.atomic():
                asistente_id = int(data["IdAsistente"])
                tipo_abono_id = int(data["IdTipoAbono"])
                edicion_id = int(data["IdEdicion"])
                pago_exitoso = data.get("PagoExitoso", True)

                tipo_abono = TipoAbono.objects.filter(id_tipo_abono=tipo_abono_id).first()
                if not tipo_abono:
                    return _error("Error: El tipo de abono indicado no existe.")

                asis = Asistente.objects.filter(id_asistente=asistente_id).first()
                if not asis:
                    return _error("Error: El asistente indicado no existe.")

                edicion = Edicion.objects.filter(id_edicion=edicion_id).first()
                if not edicion:
                    return _error("Error: La edicion indicada no existe.")

                # Generate code
                anio_actual = timezone.now().year
                codigo_valido = False
                intentos = 0
                codigo = ""
                while not codigo_valido and intentos < 100:
                    rand_num = random.randint(10000, 99999)
                    codigo = f"AB-{anio_actual}-{rand_num}"
                    if not Abono.objects.filter(codigo_acceso=codigo).exists():
                        codigo_valido = True
                    intentos += 1

                if not pago_exitoso:
                    return _error("Error: Pasarela de pago fallida. Operacion cancelada.")

                Abono.objects.create(
                    asistente=asis,
                    tipo_abono=tipo_abono,
                    edicion=edicion,
                    codigo_acceso=codigo,
                    pagado=True
                )
                return _json({"message": f"Abono registrado. Cod. acceso: {codigo}"}, 201)
        except Exception as e:
            return _error(str(e).split("\n")[0])


# --- SEDES ---
@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def sedes(request, id=None):
    if request.method == "GET":
        if id:
            r = Sede.objects.filter(id_sede=id).first()
            return _json(serialize_sede(r)) if r else _not_found()
        
        queryset = Sede.objects.all().order_by('nombre_sede')
        return _json([serialize_sede(s) for s in queryset])

    if request.method == "POST":
        data = _body(request)
        sede = Sede.objects.create(
            nombre_sede=data["NombreSede"],
            direccion=data.get("Direccion"),
            ciudad=data.get("Ciudad"),
            sitio_web=data.get("SitioWeb")
        )
        return _json({"id": sede.id_sede}, 201)

    if request.method == "DELETE":
        with transaction.atomic():
            sede = Sede.objects.filter(id_sede=id).first()
            if not sede:
                return _not_found()
            sede.delete()
            return _json({"message": "Eliminada"})


# --- SALAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def salas(request, id=None):
    if request.method == "GET":
        if id:
            r = Sala.objects.select_related('sede').filter(id_sala=id).first()
            return _json(serialize_sala(r)) if r else _not_found()
        
        queryset = Sala.objects.select_related('sede').all().order_by('sede__nombre_sede', 'nombre_sala')
        return _json([serialize_sala(s) for s in queryset])

    if request.method == "POST":
        data = _body(request)
        sala = Sala.objects.create(
            nombre_sala=data["NombreSala"],
            capacidad=data["Capacidad"],
            sede_id=data["IdSede"]
        )
        return _json({"id": sala.id_sala}, 201)


# --- EVENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def eventos(request, id=None):
    if request.method == "GET":
        if id:
            r = EventoParalelo.objects.select_related('edicion').prefetch_related('expositores').filter(id_evento=id).first()
            return _json(serialize_evento(r)) if r else _not_found()
        
        queryset = EventoParalelo.objects.select_related('edicion').prefetch_related('expositores').all().order_by('fecha_hora')
        return _json([serialize_evento(e) for e in queryset])

    if request.method == "POST":
        data = _body(request)
        with transaction.atomic():
            evento = EventoParalelo.objects.create(
                edicion_id=data["IdEdicion"],
                nombre_evento=data["NombreEvento"],
                tipo_evento=data["TipoEvento"],
                fecha_hora=data["FechaHora"],
                aforo=data["Aforo"],
                costo_inscripcion=data.get("CostoInscripcion", 0.0)
            )
            if "expositores" in data:
                evento.expositores.set(data["expositores"])
            return _json({"id": evento.id_evento}, 201)


# --- GENEROS ---
@csrf_exempt
@require_http_methods(["GET"])
def generos(request):
    queryset = Genero.objects.all().order_by('nombre_genero')
    return _json([serialize_genero(g) for g in queryset])


# --- PERSONAL ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def personal(request, id=None):
    if request.method == "GET":
        if id:
            r = Personal.objects.filter(id_personal=id).first()
            return _json(serialize_personal(r)) if r else _not_found()
        
        queryset = Personal.objects.all().order_by('nombre')
        return _json([serialize_personal(p) for p in queryset])

    if request.method == "POST":
        data = _body(request)
        pers = Personal.objects.create(
            nombre=data["Nombre"],
            biografia=data.get("Biografia"),
            email=data.get("Email"),
            telefono=data.get("Telefono"),
            nacionalidad=data.get("Nacionalidad")
        )
        return _json({"id": pers.id_personal}, 201)


# --- CATEGORIAS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def categorias(request, id=None):
    if request.method == "GET":
        if id:
            r = Categoria.objects.filter(id_categoria=id).first()
            return _json(serialize_categoria(r)) if r else _not_found()
        
        queryset = Categoria.objects.all().order_by('nombre_categoria')
        return _json([serialize_categoria(c) for c in queryset])

    if request.method == "POST":
        data = _body(request)
        cat = Categoria.objects.create(
            nombre_categoria=data["NombreCategoria"],
            descripcion=data.get("Descripcion")
        )
        return _json({"id": cat.id_categoria}, 201)


# --- JURADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def jurados(request, id=None):
    if request.method == "GET":
        if id:
            r = MiembroJurado.objects.filter(id_miembro=id).first()
            return _json(serialize_jurado(r)) if r else _not_found()
        
        queryset = MiembroJurado.objects.all().order_by('nombre')
        return _json([serialize_jurado(j) for j in queryset])

    if request.method == "POST":
        data = _body(request)
        mj = MiembroJurado.objects.create(
            nombre=data["Nombre"],
            profesion=data.get("Profesion"),
            pais=data.get("Pais"),
            email=data.get("Email")
        )
        return _json({"id": mj.id_miembro}, 201)


# --- EVALUACIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def evaluaciones(request, id=None):
    if request.method == "GET":
        if id:
            r = Evaluacion.objects.select_related(
                'miembro', 'pelicula', 'categoria', 'edicion'
            ).filter(id_evaluacion=id).first()
            return _json(serialize_evaluacion(r)) if r else _not_found()
        
        queryset = Evaluacion.objects.select_related(
            'miembro', 'pelicula', 'categoria', 'edicion'
        ).all().order_by('id_evaluacion')
        return _json([serialize_evaluacion(e) for e in queryset])

    if request.method == "POST":
        data = _body(request)
        evaluacion = Evaluacion.objects.create(
            miembro_id=data["IdMiembro"],
            pelicula_id=data["IdPelicula"],
            categoria_id=data["IdCategoria"],
            edicion_id=data["IdEdicion"],
            puntuacion=data["Puntuacion"],
            comentario=data.get("Comentario")
        )
        return _json({"id": evaluacion.id_evaluacion}, 201)


# --- PATROCINADORES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def patrocinadores(request, id=None):
    if request.method == "GET":
        if id:
            r = Patrocinador.objects.filter(id_patrocinador=id).first()
            return _json(serialize_patrocinador(r)) if r else _not_found()
        
        queryset = Patrocinador.objects.all().order_by('nombre_empresa')
        return _json([serialize_patrocinador(p) for p in queryset])

    if request.method == "POST":
        data = _body(request)
        patr = Patrocinador.objects.create(
            nombre_empresa=data["NombreEmpresa"],
            contacto=data.get("Contacto"),
            email=data.get("Email"),
            redes_sociales=data.get("RedesSociales")
        )
        return _json({"id": patr.id_patrocinador}, 201)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def patrocinios(request):
    if request.method == "GET":
        queryset = PatrocinioEdicion.objects.select_related(
            'patrocinador', 'edicion'
        ).all().order_by('-edicion__anio')
        return _json([serialize_patrocinio(p) for p in queryset])

    if request.method == "POST":
        data = _body(request)
        patr = PatrocinioEdicion.objects.create(
            patrocinador_id=data["IdPatrocinador"],
            edicion_id=data["IdEdicion"],
            tipo_aporte=data["TipoAporte"],
            monto=data.get("Monto"),
            descripcion_aporte=data.get("DescripcionAporte")
        )
        return _json({"id": patr.id_patrocinio}, 201)


# --- EDICIONES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def ediciones(request, id=None):
    if request.method == "GET":
        if id:
            r = Edicion.objects.filter(id_edicion=id).first()
            return _json(serialize_edicion(r)) if r else _not_found()
        
        queryset = Edicion.objects.all().order_by('-anio')
        return _json([serialize_edicion(e) for e in queryset])

    if request.method == "POST":
        data = _body(request)
        edi = Edicion.objects.create(
            anio=data["Anio"],
            nombre_edicion=data["NombreEdicion"],
            fecha_inicio=data["FechaInicio"],
            fecha_fin=data["FechaFin"]
        )
        return _json({"id": edi.id_edicion}, 201)


# --- HOTELES ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def hoteles(request, id=None):
    if request.method == "GET":
        if id:
            r = Hotel.objects.filter(id_hotel=id).first()
            return _json(serialize_hotel(r)) if r else _not_found()
        
        queryset = Hotel.objects.all().order_by('nombre_hotel')
        return _json([serialize_hotel(h) for h in queryset])

    if request.method == "POST":
        data = _body(request)
        hotel = Hotel.objects.create(
            nombre_hotel=data["NombreHotel"],
            direccion=data.get("Direccion"),
            estrellas=data.get("Estrellas")
        )
        return _json({"id": hotel.id_hotel}, 201)


# --- ALOJAMIENTOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def alojamientos(request, id=None):
    if request.method == "GET":
        if id:
            r = Alojamiento.objects.select_related(
                'personal', 'hotel'
            ).filter(id_alojamiento=id).first()
            return _json(serialize_alojamiento(r)) if r else _not_found()
        
        queryset = Alojamiento.objects.select_related(
            'personal', 'hotel'
        ).all().order_by('check_in')
        return _json([serialize_alojamiento(a) for a in queryset])

    if request.method == "POST":
        data = _body(request)
        aloj = Alojamiento.objects.create(
            personal_id=data["IdPersonal"],
            hotel_id=data["IdHotel"],
            edicion_id=data["IdEdicion"],
            nro_habitacion=data["NroHabitacion"],
            check_in=data["CheckIn"],
            check_out=data["CheckOut"]
        )
        return _json({"id": aloj.id_alojamiento}, 201)


# --- TRASLADOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def traslados(request, id=None):
    if request.method == "GET":
        if id:
            r = Traslado.objects.select_related('personal').filter(id_traslado=id).first()
            return _json(serialize_traslado(r)) if r else _not_found()
        
        queryset = Traslado.objects.select_related('personal').all().order_by('fecha_hora')
        return _json([serialize_traslado(t) for t in queryset])

    if request.method == "POST":
        data = _body(request)
        tras = Traslado.objects.create(
            personal_id=data["IdPersonal"],
            edicion_id=data["IdEdicion"],
            tipo_traslado=data["TipoTraslado"],
            origen=data["Origen"],
            destino=data["Destino"],
            fecha_hora=data["FechaHora"],
            nro_vuelo=data.get("NroVuelo")
        )
        return _json({"id": tras.id_traslado}, 201)


# --- PREMIOS ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def premios(request, id=None):
    if request.method == "GET":
        if id:
            r = Premio.objects.select_related(
                'categoria', 'pelicula', 'edicion'
            ).filter(id_premio=id).first()
            return _json(serialize_premio(r)) if r else _not_found()
        
        queryset = Premio.objects.select_related(
            'categoria', 'pelicula', 'edicion'
        ).all().order_by('-edicion__anio', 'categoria__nombre_categoria')
        return _json([serialize_premio(p) for p in queryset])

    if request.method == "POST":
        data = _body(request)
        premio = Premio.objects.create(
            categoria_id=data["IdCategoria"],
            pelicula_id=data["IdPelicula"],
            edicion_id=data["IdEdicion"]
        )
        return _json({"id": premio.id_premio}, 201)


# --- TARIFAS ---
@csrf_exempt
@require_http_methods(["GET"])
def tarifas(request):
    queryset = Tarifa.objects.all().order_by('-precio')
    return _json([serialize_tarifa(t) for t in queryset])


# --- TIPOS ABONO ---
@csrf_exempt
@require_http_methods(["GET"])
def tiposabono(request):
    queryset = TipoAbono.objects.all()
    return _json([serialize_tipo_abono(t) for t in queryset])


# --- COMPETENCIA PELICULA ---
@csrf_exempt
@require_http_methods(["GET", "POST"])
def competencia(request):
    if request.method == "GET":
        pelicula_id = request.GET.get("pelicula")
        categoria_id = request.GET.get("categoria")
        edicion_id = request.GET.get("edicion")
        if pelicula_id and categoria_id and edicion_id:
            r = CompetenciaPelicula.objects.select_related(
                'pelicula', 'categoria', 'edicion'
            ).filter(
                pelicula_id=pelicula_id,
                categoria_id=categoria_id,
                edicion_id=edicion_id
            ).first()
            return _json(serialize_competencia(r)) if r else _not_found()
        
        queryset = CompetenciaPelicula.objects.select_related(
            'pelicula', 'categoria', 'edicion'
        ).all().order_by('pelicula__titulo', 'categoria__nombre_categoria')
        return _json([serialize_competencia(cp) for cp in queryset])

    if request.method == "POST":
        data = _body(request)
        cp = CompetenciaPelicula.objects.create(
            pelicula_id=data["IdPelicula"],
            categoria_id=data["IdCategoria"],
            edicion_id=data["IdEdicion"]
        )
        return _json({"id": cp.pelicula.id_pelicula}, 201)


# --- REPORTES ---
@csrf_exempt
@require_http_methods(["GET"])
def reporte_ranking(request):
    id_edicion = request.GET.get("id_edicion")
    
    # Prefetch projections with their associated entries and salas
    peliculas = Pelicula.objects.prefetch_related('proyeccion_set__entrada_set', 'proyeccion_set__sala')
    if id_edicion:
        peliculas = peliculas.filter(proyeccion__edicion_id=id_edicion).distinct()
    else:
        peliculas = peliculas.filter(proyeccion__isnull=False).distinct()

    results = []
    for p in peliculas:
        proys = p.proyeccion_set.all()
        if id_edicion:
            proys = [pr for pr in proys if pr.edicion_id == int(id_edicion)]

        asistentes = sum(pr.entrada_set.count() for pr in proys)
        capacidad_total = sum(pr.sala.capacidad for pr in proys)
        pct = round((asistentes * 100.0 / capacidad_total), 2) if capacidad_total > 0 else 0.0
        results.append({
            'Titulo': p.titulo,
            'Asistentes': asistentes,
            'CapacidadTotal': capacidad_total,
            'PctOcupacion': pct
        })
    results.sort(key=lambda x: x['Asistentes'], reverse=True)
    return _json(results)


@csrf_exempt
@require_http_methods(["GET"])
def reporte_premiacion(request):
    id_edicion = request.GET.get("id_edicion")
    
    # OuterRef / Subquery to get the average evaluation score for each category/movie/edition combination
    avg_eval = Evaluacion.objects.filter(
        pelicula=OuterRef('pelicula'),
        categoria=OuterRef('categoria'),
        edicion=OuterRef('edicion')
    ).values('pelicula', 'categoria', 'edicion').annotate(avg=Avg('puntuacion')).values('avg')

    premios = Premio.objects.select_related('categoria', 'pelicula', 'edicion').annotate(
        promedio_jurado=Subquery(avg_eval)
    )
    if id_edicion:
        premios = premios.filter(edicion_id=id_edicion)

    results = [
        {
            'NombreCategoria': pre.categoria.nombre_categoria,
            'PeliculaGanadora': pre.pelicula.titulo,
            'PromedioJurado': round(float(pre.promedio_jurado), 2) if pre.promedio_jurado is not None else 0.0,
            'Anio': pre.edicion.anio
        }
        for pre in premios
    ]
    results.sort(key=lambda x: x['NombreCategoria'])
    return _json(results)


@csrf_exempt
@require_http_methods(["GET"])
def reporte_financiero(request):
    id_edicion = request.GET.get("id_edicion")
    entradas_qs = Entrada.objects.all()
    if id_edicion:
        entradas_qs = entradas_qs.filter(proyeccion__edicion_id=id_edicion)

    entradas_summary = entradas_qs.values('tarifa__nombre_tarifa').annotate(
        cantidad=Count('id_entrada'),
        subtotal=Sum('tarifa__precio')
    ).order_by('-subtotal')

    results = [
        {
            'NombreTarifa': item['tarifa__nombre_tarifa'],
            'Cantidad': item['cantidad'],
            'Subtotal': float(item['subtotal']) if item['subtotal'] is not None else 0.0
        }
        for item in entradas_summary
    ]
    return _json(results)


@csrf_exempt
@require_http_methods(["GET"])
def reporte_ocupacion(request):
    salas_qs = Sala.objects.select_related('sede').annotate(
        entradas_vendidas=Count('proyeccion__entrada')
    )

    results = []
    for s in salas_qs:
        pct = round((s.entradas_vendidas * 100.0 / s.capacidad), 2) if s.capacidad > 0 else 0.0
        results.append({
            'NombreSala': s.nombre_sala,
            'NombreSede': s.sede.nombre_sede,
            'Capacidad': s.capacidad,
            'EntradasVendidas': s.entradas_vendidas,
            'PorcentajeOcupacion': pct
        })
    results.sort(key=lambda x: x['PorcentajeOcupacion'], reverse=True)
    return _json(results)


@csrf_exempt
@require_http_methods(["GET"])
def reporte_ventas_edicion(request, id):
    ent_res = Entrada.objects.filter(proyeccion__edicion_id=id).aggregate(
        cantidad=Count('id_entrada'),
        total=Sum('tarifa__precio')
    )
    abo_res = Abono.objects.filter(pagado=True, edicion_id=id).aggregate(
        cantidad=Count('id_abono'),
        total=Sum('tipo_abono__precio')
    )

    ent_data = {
        'Cantidad': ent_res['cantidad'] or 0,
        'Total': float(ent_res['total']) if ent_res['total'] is not None else 0.0
    }
    abo_data = {
        'Cantidad': abo_res['cantidad'] or 0,
        'Total': float(abo_res['total']) if abo_res['total'] is not None else 0.0
    }

    return _json({
        "entradas": ent_data,
        "abonos": abo_data
    })
