from django.db import models


# ---------------------------------------------------------------------------
# TABLAS BASE (managed=False → la BD ya existe)
# ---------------------------------------------------------------------------

class Genero(models.Model):
    IdGenero = models.AutoField(primary_key=True, db_column='idgenero')
    NombreGenero = models.CharField(unique=True, max_length=30, db_column='nombregenero')

    class Meta:
        managed = False
        db_table = 'generos'


class Pelicula(models.Model):
    IdPelicula = models.AutoField(primary_key=True, db_column='idpelicula')
    Titulo = models.CharField(max_length=150, db_column='titulo')
    AnioProd = models.IntegerField(db_column='anioprod')
    Duracion = models.IntegerField(db_column='duracion')
    PaisOrigen = models.CharField(max_length=60, db_column='paisorigen')
    Sinopsis = models.TextField(blank=True, null=True, db_column='sinopsis')
    Clasificacion = models.CharField(max_length=10, db_column='clasificacion')
    Formato = models.CharField(max_length=10, db_column='formato')
    Estado = models.CharField(max_length=15, db_column='estado')

    class Meta:
        managed = False
        db_table = 'peliculas'


class PeliculaGenero(models.Model):
    IdPelicula = models.IntegerField(primary_key=True, db_column='idpelicula')
    IdGenero = models.IntegerField(db_column='idgenero')

    class Meta:
        managed = False
        db_table = 'peliculagenero'
        unique_together = (('IdPelicula', 'IdGenero'),)


class Personal(models.Model):
    IdPersonal = models.AutoField(primary_key=True, db_column='idpersonal')
    Nombre = models.CharField(max_length=100, db_column='nombre')
    Biografia = models.TextField(blank=True, null=True, db_column='biografia')
    Email = models.CharField(max_length=100, blank=True, null=True, db_column='email')
    Telefono = models.CharField(max_length=20, blank=True, null=True, db_column='telefono')
    Nacionalidad = models.CharField(max_length=60, blank=True, null=True, db_column='nacionalidad')

    class Meta:
        managed = False
        db_table = 'personal'


class RolesPelicula(models.Model):
    IdPersonal = models.IntegerField(primary_key=True, db_column='idpersonal')
    IdPelicula = models.IntegerField(db_column='idpelicula')
    Rol = models.CharField(max_length=20, db_column='rol')

    class Meta:
        managed = False
        db_table = 'rolespelicula'
        unique_together = (('IdPersonal', 'IdPelicula', 'Rol'),)


class Edicion(models.Model):
    IdEdicion = models.AutoField(primary_key=True, db_column='idedicion')
    Anio = models.IntegerField(unique=True, db_column='anio')
    NombreEdicion = models.CharField(max_length=100, blank=True, null=True, db_column='nombreedicion')
    FechaInicio = models.DateField(db_column='fechainicio')
    FechaFin = models.DateField(db_column='fechafin')

    class Meta:
        managed = False
        db_table = 'ediciones'


class Sede(models.Model):
    IdSede = models.AutoField(primary_key=True, db_column='idsede')
    NombreSede = models.CharField(max_length=100, db_column='nombresede')
    Direccion = models.CharField(max_length=200, blank=True, null=True, db_column='direccion')
    Ciudad = models.CharField(max_length=60, blank=True, null=True, db_column='ciudad')
    SitioWeb = models.CharField(max_length=100, blank=True, null=True, db_column='sitioweb')

    class Meta:
        managed = False
        db_table = 'sedes'


class Sala(models.Model):
    IdSala = models.AutoField(primary_key=True, db_column='idsala')
    NombreSala = models.CharField(max_length=60, db_column='nombresala')
    Capacidad = models.IntegerField(db_column='capacidad')
    IdSede = models.ForeignKey('Sede', on_delete=models.DO_NOTHING, db_column='idsede')

    class Meta:
        managed = False
        db_table = 'salas'


class Proyeccion(models.Model):
    IdProyeccion = models.AutoField(primary_key=True, db_column='idproyeccion')
    IdPelicula = models.ForeignKey('Pelicula', on_delete=models.DO_NOTHING, db_column='idpelicula', related_name='proyecciones')
    IdSala = models.ForeignKey('Sala', on_delete=models.DO_NOTHING, db_column='idsala', related_name='proyecciones_sala')
    IdEdicion = models.ForeignKey('Edicion', on_delete=models.DO_NOTHING, db_column='idedicion')
    FechaHora = models.DateTimeField(db_column='fechahora')
    TieneQA = models.BooleanField(blank=True, null=True, db_column='tieneqa')
    AforoDisponible = models.IntegerField(db_column='aforodisponible')

    class Meta:
        managed = False
        db_table = 'proyecciones'


class EventoParalelo(models.Model):
    IdEvento = models.AutoField(primary_key=True, db_column='idevento')
    IdEdicion = models.ForeignKey('Edicion', on_delete=models.DO_NOTHING, db_column='idedicion')
    NombreEvento = models.CharField(max_length=150, db_column='nombreevento')
    TipoEvento = models.CharField(max_length=15, db_column='tipoevento')
    FechaHora = models.DateTimeField(db_column='fechahora')
    Aforo = models.IntegerField(db_column='aforo')
    CostoInscripcion = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_column='costoinscripcion')

    class Meta:
        managed = False
        db_table = 'eventosparalelos'


class ExpositorEvento(models.Model):
    IdEvento = models.IntegerField(primary_key=True, db_column='idevento')
    IdPersonal = models.IntegerField(db_column='idpersonal')

    class Meta:
        managed = False
        db_table = 'expositorevento'
        unique_together = (('IdEvento', 'IdPersonal'),)


class Categoria(models.Model):
    IdCategoria = models.AutoField(primary_key=True, db_column='idcategoria')
    NombreCategoria = models.CharField(max_length=80, db_column='nombrecategoria')
    Descripcion = models.CharField(max_length=200, blank=True, null=True, db_column='descripcion')

    class Meta:
        managed = False
        db_table = 'categorias'


class MiembroJurado(models.Model):
    IdMiembro = models.AutoField(primary_key=True, db_column='idmiembro')
    Nombre = models.CharField(max_length=100, db_column='nombre')
    Profesion = models.CharField(max_length=60, null=True, db_column='profesion')
    Pais = models.CharField(max_length=60, null=True, db_column='pais')
    Email = models.CharField(max_length=100, null=True, db_column='email')
    IdEdicion = models.ForeignKey('Edicion', on_delete=models.DO_NOTHING, db_column='idedicion', null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'miembrosjurado'


class JuradoCategoria(models.Model):
    IdMiembro = models.IntegerField(primary_key=True, db_column='idmiembro')
    IdCategoria = models.IntegerField(db_column='idcategoria')

    class Meta:
        managed = False
        db_table = 'juradocategoria'
        unique_together = (('IdMiembro', 'IdCategoria'),)


class CompetenciaPelicula(models.Model):
    IdPelicula = models.IntegerField(primary_key=True, db_column='idpelicula')
    IdCategoria = models.IntegerField(db_column='idcategoria')
    IdEdicion = models.IntegerField(db_column='idedicion')

    class Meta:
        managed = False
        db_table = 'competenciapelicula'
        unique_together = (('IdPelicula', 'IdCategoria', 'IdEdicion'),)


class Evaluacion(models.Model):
    IdEvaluacion = models.AutoField(primary_key=True, db_column='idevaluacion')
    IdMiembro = models.IntegerField(db_column='idmiembro')
    IdPelicula = models.IntegerField(db_column='idpelicula')
    IdCategoria = models.IntegerField(db_column='idcategoria')
    IdEdicion = models.IntegerField(db_column='idedicion')
    Puntuacion = models.IntegerField(db_column='puntuacion')
    Comentario = models.TextField(blank=True, null=True, db_column='comentario')

    class Meta:
        managed = False
        db_table = 'evaluaciones'
        unique_together = (('IdMiembro', 'IdPelicula', 'IdCategoria', 'IdEdicion'),)


class Premio(models.Model):
    IdPremio = models.AutoField(primary_key=True, db_column='idpremio')
    IdCategoria = models.ForeignKey('Categoria', on_delete=models.DO_NOTHING, db_column='idcategoria')
    IdPelicula = models.ForeignKey('Pelicula', on_delete=models.DO_NOTHING, db_column='idpelicula')
    IdEdicion = models.ForeignKey('Edicion', on_delete=models.DO_NOTHING, db_column='idedicion')

    class Meta:
        managed = False
        db_table = 'premios'
        unique_together = (('IdCategoria', 'IdEdicion'),)


class Asistente(models.Model):
    IdAsistente = models.AutoField(primary_key=True, db_column='idasistente')
    Nombre = models.CharField(max_length=100, db_column='nombre')
    Email = models.CharField(unique=True, max_length=100, db_column='email')
    Telefono = models.CharField(max_length=20, blank=True, null=True, db_column='telefono')
    TipoAsistente = models.CharField(max_length=15, db_column='tipoasistente')

    class Meta:
        managed = False
        db_table = 'asistentes'


class Tarifa(models.Model):
    IdTarifa = models.AutoField(primary_key=True, db_column='idtarifa')
    NombreTarifa = models.CharField(max_length=30, db_column='nombretarifa')
    Precio = models.DecimalField(max_digits=10, decimal_places=2, db_column='precio')

    class Meta:
        managed = False
        db_table = 'tarifas'


class Entrada(models.Model):
    IdEntrada = models.AutoField(primary_key=True, db_column='identrada')
    IdAsistente = models.ForeignKey('Asistente', on_delete=models.DO_NOTHING, db_column='idasistente')
    IdProyeccion = models.ForeignKey('Proyeccion', on_delete=models.DO_NOTHING, db_column='idproyeccion', null=True, blank=True, related_name='entradas')
    IdEvento = models.IntegerField(blank=True, null=True, db_column='idevento')
    IdTarifa = models.ForeignKey('Tarifa', on_delete=models.DO_NOTHING, db_column='idtarifa')
    FechaCompra = models.DateTimeField(db_column='fechacompra')

    class Meta:
        managed = False
        db_table = 'entradas'


class TipoAbono(models.Model):
    IdTipoAbono = models.AutoField(primary_key=True, db_column='idtipoabono')
    NombreAbono = models.CharField(max_length=60, db_column='nombreabono')
    Descripcion = models.CharField(max_length=200, blank=True, null=True, db_column='descripcion')
    Precio = models.DecimalField(max_digits=10, decimal_places=2, db_column='precio')

    class Meta:
        managed = False
        db_table = 'tiposabono'


class Abono(models.Model):
    IdAbono = models.AutoField(primary_key=True, db_column='idabono')
    IdAsistente = models.IntegerField(db_column='idasistente')
    IdTipoAbono = models.ForeignKey('TipoAbono', on_delete=models.DO_NOTHING, db_column='idtipoabono')
    IdEdicion = models.ForeignKey('Edicion', on_delete=models.DO_NOTHING, db_column='idedicion')
    FechaCompra = models.DateTimeField(db_column='fechacompra')
    CodigoAcceso = models.CharField(unique=True, max_length=20, db_column='codigoacceso')
    Pagado = models.BooleanField(db_column='pagado')

    class Meta:
        managed = False
        db_table = 'abonos'
        unique_together = (('IdAsistente', 'IdTipoAbono'),)


class Hotel(models.Model):
    IdHotel = models.AutoField(primary_key=True, db_column='idhotel')
    NombreHotel = models.CharField(max_length=100, db_column='nombrehotel')
    Direccion = models.CharField(max_length=200, blank=True, null=True, db_column='direccion')
    Estrellas = models.IntegerField(blank=True, null=True, db_column='estrellas')

    class Meta:
        managed = False
        db_table = 'hoteles'


class Alojamiento(models.Model):
    IdAlojamiento = models.AutoField(primary_key=True, db_column='idalojamiento')
    IdPersonal = models.IntegerField(db_column='idpersonal')
    IdHotel = models.IntegerField(db_column='idhotel')
    IdEdicion = models.IntegerField(db_column='idedicion')
    NroHabitacion = models.CharField(max_length=10, db_column='nrohabitacion')
    CheckIn = models.DateField(db_column='checkin')
    CheckOut = models.DateField(db_column='checkout')

    class Meta:
        managed = False
        db_table = 'alojamientos'


class Traslado(models.Model):
    IdTraslado = models.AutoField(primary_key=True, db_column='idtraslado')
    IdPersonal = models.IntegerField(db_column='idpersonal')
    IdEdicion = models.IntegerField(db_column='idedicion')
    TipoTraslado = models.CharField(max_length=10, db_column='tipotraslado')
    Origen = models.CharField(max_length=100, db_column='origen')
    Destino = models.CharField(max_length=100, db_column='destino')
    FechaHora = models.DateTimeField(db_column='fechahora')
    NroVuelo = models.CharField(max_length=20, blank=True, null=True, db_column='nrovuelo')

    class Meta:
        managed = False
        db_table = 'traslados'


class Patrocinador(models.Model):
    IdPatrocinador = models.AutoField(primary_key=True, db_column='idpatrocinador')
    NombreEmpresa = models.CharField(max_length=100, db_column='nombreempresa')
    Contacto = models.CharField(max_length=100, blank=True, null=True, db_column='contacto')
    Email = models.CharField(max_length=100, blank=True, null=True, db_column='email')
    RedesSociales = models.CharField(max_length=150, blank=True, null=True, db_column='redessociales')

    class Meta:
        managed = False
        db_table = 'patrocinadores'


class PatrocinioEdicion(models.Model):
    IdPatrocinio = models.AutoField(primary_key=True, db_column='idpatrocinio')
    IdPatrocinador = models.IntegerField(db_column='idpatrocinador')
    IdEdicion = models.IntegerField(db_column='idedicion')
    TipoAporte = models.CharField(max_length=10, db_column='tipoaporte')
    Monto = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, db_column='monto')
    DescripcionAporte = models.CharField(max_length=200, blank=True, null=True, db_column='descripcionaporte')

    class Meta:
        managed = False
        db_table = 'patrocinioedicion'


# ---------------------------------------------------------------------------
# VISTAS (managed=False sobre las vw_*)
# ---------------------------------------------------------------------------

class VwPelicula(models.Model):
    IdPelicula = models.IntegerField(primary_key=True, db_column='idpelicula')
    Titulo = models.CharField(max_length=150, db_column='titulo')
    AnioProd = models.IntegerField(db_column='anioprod')
    Duracion = models.IntegerField(db_column='duracion')
    PaisOrigen = models.CharField(max_length=60, db_column='paisorigen')
    Clasificacion = models.CharField(max_length=10, db_column='clasificacion')
    Formato = models.CharField(max_length=10, db_column='formato')
    Estado = models.CharField(max_length=15, db_column='estado')
    Generos = models.TextField(blank=True, db_column='generos')

    class Meta:
        managed = False
        db_table = 'vw_peliculas'


class VwProyeccion(models.Model):
    IdProyeccion = models.IntegerField(primary_key=True, db_column='idproyeccion')
    IdPelicula = models.IntegerField(db_column='idpelicula')
    Titulo = models.CharField(max_length=150, db_column='titulo')
    Duracion = models.IntegerField(db_column='duracion')
    IdSala = models.IntegerField(db_column='idsala')
    NombreSala = models.CharField(max_length=60, db_column='nombresala')
    NombreSede = models.CharField(max_length=100, db_column='nombresede')
    FechaHora = models.DateTimeField(db_column='fechahora')
    AforoDisponible = models.IntegerField(db_column='aforodisponible')
    Capacidad = models.IntegerField(db_column='capacidad')
    TieneQA = models.BooleanField(blank=True, null=True, db_column='tieneqa')
    IdEdicion = models.IntegerField(db_column='idedicion')
    Anio = models.IntegerField(db_column='anio')
    NombreEdicion = models.CharField(max_length=100, blank=True, null=True, db_column='nombreedicion')

    class Meta:
        managed = False
        db_table = 'vw_proyecciones'


class VwAsistente(models.Model):
    IdAsistente = models.IntegerField(primary_key=True, db_column='idasistente')
    Nombre = models.CharField(max_length=100, db_column='nombre')
    Email = models.CharField(max_length=100, db_column='email')
    TipoAsistente = models.CharField(max_length=15, db_column='tipoasistente')

    class Meta:
        managed = False
        db_table = 'vw_asistentes'


class VwEntrada(models.Model):
    IdEntrada = models.IntegerField(primary_key=True, db_column='identrada')
    IdAsistente = models.IntegerField(db_column='idasistente')
    IdProyeccion = models.IntegerField(blank=True, null=True, db_column='idproyeccion')
    IdEvento = models.IntegerField(blank=True, null=True, db_column='idevento')
    IdTarifa = models.IntegerField(db_column='idtarifa')
    FechaCompra = models.DateTimeField(db_column='fechacompra')
    Asistente = models.CharField(max_length=100, db_column='asistente')
    Pelicula = models.CharField(max_length=150, blank=True, null=True, db_column='pelicula')
    FechaHora = models.DateTimeField(blank=True, null=True, db_column='fechahora')

    class Meta:
        managed = False
        db_table = 'vw_entradas'


class VwPersonal(models.Model):
    IdPersonal = models.IntegerField(primary_key=True, db_column='idpersonal')
    Nombre = models.CharField(max_length=100, db_column='nombre')
    Biografia = models.TextField(blank=True, null=True, db_column='biografia')
    Email = models.CharField(max_length=100, blank=True, null=True, db_column='email')
    Telefono = models.CharField(max_length=20, blank=True, null=True, db_column='telefono')
    Nacionalidad = models.CharField(max_length=60, blank=True, null=True, db_column='nacionalidad')

    class Meta:
        managed = False
        db_table = 'vw_personal'


class VwEvaluacion(models.Model):
    IdEvaluacion = models.IntegerField(primary_key=True, db_column='idevaluacion')
    IdMiembro = models.IntegerField(db_column='idmiembro')
    IdPelicula = models.IntegerField(db_column='idpelicula')
    IdCategoria = models.IntegerField(db_column='idcategoria')
    Puntuacion = models.IntegerField(db_column='puntuacion')
    Comentario = models.TextField(blank=True, null=True, db_column='comentario')
    Jurado = models.CharField(max_length=100, db_column='jurado')
    Pelicula = models.CharField(max_length=150, db_column='pelicula')
    Categoria = models.CharField(max_length=80, db_column='categoria')

    class Meta:
        managed = False
        db_table = 'vw_evaluaciones'


class VwEvento(models.Model):
    IdEvento = models.IntegerField(primary_key=True, db_column='idevento')
    IdEdicion = models.IntegerField(db_column='idedicion')
    NombreEvento = models.CharField(max_length=150, db_column='nombreevento')
    TipoEvento = models.CharField(max_length=15, db_column='tipoevento')
    FechaHora = models.DateTimeField(db_column='fechahora')
    Aforo = models.IntegerField(db_column='aforo')
    CostoInscripcion = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_column='costoinscripcion')
    Anio = models.IntegerField(db_column='anio')
    NombreEdicion = models.CharField(max_length=100, blank=True, null=True, db_column='nombreedicion')
    Expositores = models.TextField(blank=True, db_column='expositores')

    class Meta:
        managed = False
        db_table = 'vw_eventos'


class VwAbono(models.Model):
    IdAbono = models.IntegerField(primary_key=True, db_column='idabono')
    IdAsistente = models.IntegerField(db_column='idasistente')
    IdTipoAbono = models.IntegerField(db_column='idtipoabono')
    IdEdicion = models.IntegerField(db_column='idedicion')
    FechaCompra = models.DateTimeField(db_column='fechacompra')
    CodigoAcceso = models.CharField(max_length=20, db_column='codigoacceso')
    Pagado = models.BooleanField(db_column='pagado')
    NombreAsistente = models.CharField(max_length=100, db_column='nombreasistente')
    NombreAbono = models.CharField(max_length=60, db_column='nombreabono')
    Precio = models.DecimalField(max_digits=10, decimal_places=2, db_column='precio')
    Descripcion = models.CharField(max_length=200, blank=True, null=True, db_column='descripcion')
    Anio = models.IntegerField(db_column='anio')
    NombreEdicion = models.CharField(max_length=100, blank=True, null=True, db_column='nombreedicion')

    class Meta:
        managed = False
        db_table = 'vw_abonos'


class VwPremio(models.Model):
    IdPremio = models.IntegerField(primary_key=True, db_column='idpremio')
    IdCategoria = models.IntegerField(db_column='idcategoria')
    NombreCategoria = models.CharField(max_length=80, db_column='nombrecategoria')
    IdPelicula = models.IntegerField(db_column='idpelicula')
    TituloPelicula = models.CharField(max_length=150, db_column='titulopelicula')
    IdEdicion = models.IntegerField(db_column='idedicion')
    Anio = models.IntegerField(db_column='anio')
    NombreEdicion = models.CharField(max_length=100, blank=True, null=True, db_column='nombreedicion')

    class Meta:
        managed = False
        db_table = 'vw_premios'


class VwSala(models.Model):
    IdSala = models.IntegerField(primary_key=True, db_column='idsala')
    NombreSala = models.CharField(max_length=60, db_column='nombresala')
    Capacidad = models.IntegerField(db_column='capacidad')
    IdSede = models.IntegerField(db_column='idsede')
    NombreSede = models.CharField(max_length=100, db_column='nombresede')

    class Meta:
        managed = False
        db_table = 'vw_salas'


class VwTarifa(models.Model):
    IdTarifa = models.IntegerField(primary_key=True, db_column='idtarifa')
    NombreTarifa = models.CharField(max_length=30, db_column='nombretarifa')
    Precio = models.DecimalField(max_digits=10, decimal_places=2, db_column='precio')

    class Meta:
        managed = False
        db_table = 'vw_tarifas'


class VwTipoAbono(models.Model):
    IdTipoAbono = models.IntegerField(primary_key=True, db_column='idtipoabono')
    NombreAbono = models.CharField(max_length=60, db_column='nombreabono')
    Descripcion = models.CharField(max_length=200, blank=True, null=True, db_column='descripcion')
    Precio = models.DecimalField(max_digits=10, decimal_places=2, db_column='precio')

    class Meta:
        managed = False
        db_table = 'vw_tiposabono'


class VwAlojamiento(models.Model):
    IdAlojamiento = models.IntegerField(primary_key=True, db_column='idalojamiento')
    IdPersonal = models.IntegerField(db_column='idpersonal')
    IdHotel = models.IntegerField(db_column='idhotel')
    IdEdicion = models.IntegerField(db_column='idedicion')
    NroHabitacion = models.CharField(max_length=10, db_column='nrohabitacion')
    CheckIn = models.DateField(db_column='checkin')
    CheckOut = models.DateField(db_column='checkout')
    Personal = models.CharField(max_length=100, db_column='personal')
    NombreHotel = models.CharField(max_length=100, db_column='nombrehotel')

    class Meta:
        managed = False
        db_table = 'vw_alojamientos'


class VwTraslado(models.Model):
    IdTraslado = models.IntegerField(primary_key=True, db_column='idtraslado')
    IdPersonal = models.IntegerField(db_column='idpersonal')
    IdEdicion = models.IntegerField(db_column='idedicion')
    TipoTraslado = models.CharField(max_length=10, db_column='tipotraslado')
    Origen = models.CharField(max_length=100, db_column='origen')
    Destino = models.CharField(max_length=100, db_column='destino')
    FechaHora = models.DateTimeField(db_column='fechahora')
    NroVuelo = models.CharField(max_length=20, blank=True, null=True, db_column='nrovuelo')
    Personal = models.CharField(max_length=100, db_column='personal')

    class Meta:
        managed = False
        db_table = 'vw_traslados'


class VwPatrocinio(models.Model):
    IdPatrocinio = models.IntegerField(primary_key=True, db_column='idpatrocinio')
    IdPatrocinador = models.IntegerField(db_column='idpatrocinador')
    IdEdicion = models.IntegerField(db_column='idedicion')
    TipoAporte = models.CharField(max_length=10, db_column='tipoaporte')
    Monto = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, db_column='monto')
    DescripcionAporte = models.CharField(max_length=200, blank=True, null=True, db_column='descripcionaporte')
    NombreEmpresa = models.CharField(max_length=100, db_column='nombreempresa')
    NombreEdicion = models.CharField(max_length=100, blank=True, null=True, db_column='nombreedicion')
    Anio = models.IntegerField(db_column='anio')

    class Meta:
        managed = False
        db_table = 'vw_patrocinios'


class VwCompetencia(models.Model):
    IdPelicula = models.IntegerField(primary_key=True, db_column='idpelicula')
    IdCategoria = models.IntegerField(db_column='idcategoria')
    IdEdicion = models.IntegerField(db_column='idedicion')
    Titulo = models.CharField(max_length=150, db_column='titulo')
    NombreCategoria = models.CharField(max_length=80, db_column='nombrecategoria')

    class Meta:
        managed = False
        db_table = 'vw_competencia'


class VwRolesPelicula(models.Model):
    IdPersonal = models.IntegerField(primary_key=True, db_column='idpersonal')
    IdPelicula = models.IntegerField(db_column='idpelicula')
    Rol = models.CharField(max_length=20, db_column='rol')
    Personal = models.CharField(max_length=100, db_column='personal')
    Pelicula = models.CharField(max_length=150, db_column='pelicula')

    class Meta:
        managed = False
        db_table = 'vw_rolespelicula'


class VwCategoriasPorJurado(models.Model):
    IdMiembro = models.IntegerField(primary_key=True, db_column='idmiembro')
    IdCategoria = models.IntegerField(db_column='idcategoria')
    NombreCategoria = models.CharField(max_length=80, db_column='nombrecategoria')

    class Meta:
        managed = False
        db_table = 'vw_categoriasporjurado'


class VwPeliculasPorCategoria(models.Model):
    IdCategoria = models.IntegerField(primary_key=True, db_column='idcategoria')
    IdPelicula = models.IntegerField(db_column='idpelicula')
    Titulo = models.CharField(max_length=150, db_column='titulo')

    class Meta:
        managed = False
        db_table = 'vw_peliculasporcategoria'
