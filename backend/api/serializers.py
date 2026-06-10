def serialize_genero(genero):
    return {
        'IdGenero': genero.id_genero,
        'NombreGenero': genero.nombre_genero,
    }


def serialize_pelicula(pelicula):
    return {
        'IdPelicula': pelicula.id_pelicula,
        'Titulo': pelicula.titulo,
        'AnioProd': pelicula.anio_prod,
        'Duracion': pelicula.duracion,
        'PaisOrigen': pelicula.pais_orig,
        'Sinopsis': pelicula.sinopsis,
        'Clasificacion': pelicula.clasificacion,
        'Formato': pelicula.formato,
        'Estado': pelicula.estado,
        'Generos': ', '.join(g.nombre_genero for g in pelicula.generos.all()),
    }


def serialize_proyeccion(proyeccion):
    return {
        'IdProyeccion': proyeccion.id_proyeccion,
        'IdPelicula': proyeccion.pelicula.id_pelicula,
        'Titulo': proyeccion.pelicula.titulo,
        'Duracion': proyeccion.pelicula.duracion,
        'IdSala': proyeccion.sala.id_sala,
        'NombreSala': proyeccion.sala.nombre_sala,
        'NombreSede': proyeccion.sala.sede.nombre_sede,
        'FechaHora': proyeccion.fecha_hora.isoformat() if proyeccion.fecha_hora else None,
        'AforoDisponible': proyeccion.aforo_disponible,
        'Capacidad': proyeccion.sala.capacidad,
        'TieneQA': proyeccion.tiene_qa,
        'IdEdicion': proyeccion.edicion.id_edicion,
        'Anio': proyeccion.edicion.anio,
        'NombreEdicion': proyeccion.edicion.nombre_edicion,
    }


def serialize_asistente(asistente):
    return {
        'IdAsistente': asistente.id_asistente,
        'Nombre': asistente.nombre,
        'Email': asistente.email,
        'Telefono': asistente.telefono,
        'TipoAsistente': asistente.tipo_asistente,
    }


def serialize_entrada(entrada):
    return {
        'IdEntrada': entrada.id_entrada,
        'IdAsistente': entrada.asistente.id_asistente,
        'IdProyeccion': entrada.proyeccion.id_proyeccion if entrada.proyeccion else None,
        'IdEvento': entrada.evento.id_evento if entrada.evento else None,
        'IdTarifa': entrada.tarifa.id_tarifa,
        'FechaCompra': entrada.fecha_compra.isoformat() if entrada.fecha_compra else None,
        'Asistente': entrada.asistente.nombre,
        'Pelicula': entrada.proyeccion.pelicula.titulo if (entrada.proyeccion and entrada.proyeccion.pelicula) else None,
        'FechaHora': entrada.proyeccion.fecha_hora.isoformat() if (entrada.proyeccion and entrada.proyeccion.fecha_hora) else None,
    }


def serialize_abono(abono):
    return {
        'IdAbono': abono.id_abono,
        'IdAsistente': abono.asistente.id_asistente,
        'NombreAsistente': abono.asistente.nombre,
        'IdTipoAbono': abono.tipo_abono.id_tipo_abono,
        'NombreAbono': abono.tipo_abono.nombre_abono,
        'Descripcion': abono.tipo_abono.descripcion,
        'Precio': float(abono.tipo_abono.precio),
        'IdEdicion': abono.edicion.id_edicion,
        'Anio': abono.edicion.anio,
        'NombreEdicion': abono.edicion.nombre_edicion,
        'CodigoAcceso': abono.codigo_acceso,
        'Pagado': abono.pagado,
        'FechaCompra': abono.fecha_compra.isoformat() if abono.fecha_compra else None,
    }


def serialize_sede(sede):
    return {
        'IdSede': sede.id_sede,
        'NombreSede': sede.nombre_sede,
        'Direccion': sede.direccion,
        'Ciudad': sede.ciudad,
        'SitioWeb': sede.sitio_web,
    }


def serialize_sala(sala):
    return {
        'IdSala': sala.id_sala,
        'NombreSala': sala.nombre_sala,
        'Capacidad': sala.capacidad,
        'IdSede': sala.sede.id_sede,
        'NombreSede': sala.sede.nombre_sede,
    }


def serialize_evento(evento):
    return {
        'IdEvento': evento.id_evento,
        'IdEdicion': evento.edicion.id_edicion,
        'NombreEvento': evento.nombre_evento,
        'TipoEvento': evento.tipo_evento,
        'FechaHora': evento.fecha_hora.isoformat() if evento.fecha_hora else None,
        'Aforo': evento.aforo,
        'CostoInscripcion': float(evento.costo_inscripcion),
        'Anio': evento.edicion.anio,
        'NombreEdicion': evento.edicion.nombre_edicion,
        'Expositores': ', '.join(e.nombre for e in evento.expositores.all()),
    }


def serialize_personal(personal):
    return {
        'IdPersonal': personal.id_personal,
        'Nombre': personal.nombre,
        'Biografia': personal.biografia,
        'Email': personal.email,
        'Telefono': personal.telefono,
        'Nacionalidad': personal.nacionalidad,
    }


def serialize_categoria(categoria):
    return {
        'IdCategoria': categoria.id_categoria,
        'NombreCategoria': categoria.nombre_categoria,
        'Descripcion': categoria.descripcion,
    }


def serialize_jurado(jurado):
    return {
        'IdMiembro': jurado.id_miembro,
        'Nombre': jurado.nombre,
        'Profesion': jurado.profesion,
        'Pais': jurado.pais,
        'Email': jurado.email,
    }


def serialize_evaluacion(evaluacion):
    return {
        'IdEvaluacion': evaluacion.id_evaluacion,
        'IdMiembro': evaluacion.miembro.id_miembro,
        'Jurado': evaluacion.miembro.nombre,
        'IdPelicula': evaluacion.pelicula.id_pelicula,
        'Pelicula': evaluacion.pelicula.titulo,
        'IdCategoria': evaluacion.categoria.id_categoria,
        'Categoria': evaluacion.categoria.nombre_categoria,
        'IdEdicion': evaluacion.edicion.id_edicion,
        'Anio': evaluacion.edicion.anio,
        'NombreEdicion': evaluacion.edicion.nombre_edicion,
        'Puntuacion': evaluacion.puntuacion,
        'Comentario': evaluacion.comentario,
    }


def serialize_patrocinador(patrocinador):
    return {
        'IdPatrocinador': patrocinador.id_patrocinador,
        'NombreEmpresa': patrocinador.nombre_empresa,
        'Contacto': patrocinador.contacto,
        'Email': patrocinador.email,
        'RedesSociales': patrocinador.redes_sociales,
    }


def serialize_patrocinio(patrocinio):
    return {
        'IdPatrocinio': patrocinio.id_patrocinio,
        'IdPatrocinador': patrocinio.patrocinador.id_patrocinador,
        'IdEdicion': patrocinio.edicion.id_edicion,
        'TipoAporte': patrocinio.tipo_aporte,
        'Monto': float(patrocinio.monto) if patrocinio.monto is not None else None,
        'DescripcionAporte': patrocinio.descripcion_aporte,
        'NombreEmpresa': patrocinio.patrocinador.nombre_empresa,
        'NombreEdicion': patrocinio.edicion.nombre_edicion,
        'Anio': patrocinio.edicion.anio,
    }


def serialize_edicion(edicion):
    return {
        'IdEdicion': edicion.id_edicion,
        'Anio': edicion.anio,
        'NombreEdicion': edicion.nombre_edicion,
        'FechaInicio': edicion.fecha_inicio.isoformat() if edicion.fecha_inicio else None,
        'FechaFin': edicion.fecha_fin.isoformat() if edicion.fecha_fin else None,
    }


def serialize_hotel(hotel):
    return {
        'IdHotel': hotel.id_hotel,
        'NombreHotel': hotel.nombre_hotel,
        'Direccion': hotel.direccion,
        'Estrellas': hotel.estrellas,
    }


def serialize_alojamiento(alojamiento):
    return {
        'IdAlojamiento': alojamiento.id_alojamiento,
        'IdPersonal': alojamiento.personal.id_personal,
        'Personal': alojamiento.personal.nombre,
        'IdHotel': alojamiento.hotel.id_hotel,
        'NombreHotel': alojamiento.hotel.nombre_hotel,
        'IdEdicion': alojamiento.edicion.id_edicion,
        'NroHabitacion': alojamiento.nro_habitacion,
        'CheckIn': alojamiento.check_in.isoformat() if alojamiento.check_in else None,
        'CheckOut': alojamiento.check_out.isoformat() if alojamiento.check_out else None,
    }


def serialize_traslado(traslado):
    return {
        'IdTraslado': traslado.id_traslado,
        'IdPersonal': traslado.personal.id_personal,
        'Personal': traslado.personal.nombre,
        'IdEdicion': traslado.edicion.id_edicion,
        'TipoTraslado': traslado.tipo_traslado,
        'Origen': traslado.origen,
        'Destino': traslado.destino,
        'FechaHora': traslado.fecha_hora.isoformat() if traslado.fecha_hora else None,
        'NroVuelo': traslado.nro_vuelo,
    }


def serialize_premio(premio):
    return {
        'IdPremio': premio.id_premio,
        'IdCategoria': premio.categoria.id_categoria,
        'NombreCategoria': premio.categoria.nombre_categoria,
        'IdPelicula': premio.pelicula.id_pelicula,
        'Pelicula': premio.pelicula.titulo,
        'IdEdicion': premio.edicion.id_edicion,
        'Anio': premio.edicion.anio,
        'NombreEdicion': premio.edicion.nombre_edicion,
    }


def serialize_tarifa(tarifa):
    return {
        'IdTarifa': tarifa.id_tarifa,
        'NombreTarifa': tarifa.nombre_tarifa,
        'Precio': float(tarifa.precio),
    }


def serialize_tipo_abono(tipo_abono):
    return {
        'IdTipoAbono': tipo_abono.id_tipo_abono,
        'NombreAbono': tipo_abono.nombre_abono,
        'Descripcion': tipo_abono.descripcion,
        'Precio': float(tipo_abono.precio),
    }


def serialize_competencia(cp):
    return {
        'IdPelicula': cp.pelicula.id_pelicula,
        'IdCategoria': cp.categoria.id_categoria,
        'IdEdicion': cp.edicion.id_edicion,
        'Titulo': cp.pelicula.titulo,
        'NombreCategoria': cp.categoria.nombre_categoria,
        'Anio': cp.edicion.anio,
        'NombreEdicion': cp.edicion.nombre_edicion,
    }
