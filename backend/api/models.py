from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Genero(models.Model):
    id_genero = models.AutoField(db_column='idgenero', primary_key=True)
    nombre_genero = models.CharField(db_column='nombregenero', unique=True, max_length=30)

    class Meta:
        db_table = 'generos'

    def __str__(self):
        return self.nombre_genero


class Pelicula(models.Model):
    CLASIFICACION_CHOICES = [
        ('G', 'G'),
        ('PG', 'PG'),
        ('PG-13', 'PG-13'),
        ('R', 'R'),
        ('NC-17', 'NC-17'),
        ('ATP', 'ATP'),
    ]
    FORMATO_CHOICES = [
        ('Digital', 'Digital'),
        ('35mm', '35mm'),
        ('IMAX', 'IMAX'),
    ]
    ESTADO_CHOICES = [
        ('Postulada', 'Postulada'),
        ('Seleccionada', 'Seleccionada'),
        ('Rechazada', 'Rechazada'),
        ('Premiada', 'Premiada'),
    ]

    id_pelicula = models.AutoField(db_column='idpelicula', primary_key=True)
    titulo = models.CharField(db_column='titulo', max_length=150)
    anio_prod = models.IntegerField(db_column='anioprod', validators=[MinValueValidator(1889)])
    duracion = models.IntegerField(db_column='duracion', validators=[MinValueValidator(1)])
    pais_orig = models.CharField(db_column='paisorigen', max_length=60)
    sinopsis = models.TextField(db_column='sinopsis', blank=True, null=True)
    clasificacion = models.CharField(db_column='clasificacion', max_length=10, choices=CLASIFICACION_CHOICES)
    formato = models.CharField(db_column='formato', max_length=10, choices=FORMATO_CHOICES)
    estado = models.CharField(db_column='estado', max_length=15, default='Postulada', choices=ESTADO_CHOICES)
    generos = models.ManyToManyField(Genero, through='PeliculaGenero', related_name='peliculas')

    class Meta:
        db_table = 'peliculas'

    def __str__(self):
        return self.titulo


class PeliculaGenero(models.Model):
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, db_column='idpelicula', primary_key=True)
    genero = models.ForeignKey(Genero, on_delete=models.CASCADE, db_column='idgenero')

    class Meta:
        db_table = 'peliculagenero'
        unique_together = (('pelicula', 'genero'),)


class Personal(models.Model):
    id_personal = models.AutoField(db_column='idpersonal', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    biografia = models.TextField(db_column='biografia', blank=True, null=True)
    email = models.CharField(db_column='email', max_length=100, blank=True, null=True)
    telefono = models.CharField(db_column='telefono', max_length=20, blank=True, null=True)
    nacionalidad = models.CharField(db_column='nacionalidad', max_length=60, blank=True, null=True)

    class Meta:
        db_table = 'personal'

    def __str__(self):
        return self.nombre


class RolPelicula(models.Model):
    ROL_CHOICES = [
        ('Director', 'Director'),
        ('Actor', 'Actor'),
        ('Guionista', 'Guionista'),
        ('Productor', 'Productor'),
    ]

    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, db_column='idpersonal', primary_key=True)
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, db_column='idpelicula')
    rol = models.CharField(db_column='rol', max_length=20, choices=ROL_CHOICES)

    class Meta:
        db_table = 'rolespelicula'
        unique_together = (('personal', 'pelicula', 'rol'),)


class Edicion(models.Model):
    id_edicion = models.AutoField(db_column='idedicion', primary_key=True)
    anio = models.IntegerField(db_column='anio', unique=True)
    nombre_edicion = models.CharField(db_column='nombreedicion', max_length=100, blank=True, null=True)
    fecha_inicio = models.DateField(db_column='fechainicio')
    fecha_fin = models.DateField(db_column='fechafin')

    class Meta:
        db_table = 'ediciones'

    def __str__(self):
        return self.nombre_edicion or str(self.anio)


class Sede(models.Model):
    id_sede = models.AutoField(db_column='idsede', primary_key=True)
    nombre_sede = models.CharField(db_column='nombresede', max_length=100)
    direccion = models.CharField(db_column='direccion', max_length=200, blank=True, null=True)
    ciudad = models.CharField(db_column='ciudad', max_length=60, blank=True, null=True)
    sitio_web = models.CharField(db_column='sitioweb', max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'sedes'

    def __str__(self):
        return self.nombre_sede


class Sala(models.Model):
    id_sala = models.AutoField(db_column='idsala', primary_key=True)
    nombre_sala = models.CharField(db_column='nombresala', max_length=60)
    capacidad = models.IntegerField(db_column='capacidad', validators=[MinValueValidator(1)])
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, db_column='idsede')

    class Meta:
        db_table = 'salas'

    def __str__(self):
        return f"{self.sede.nombre_sede} - {self.nombre_sala}"


class Proyeccion(models.Model):
    id_proyeccion = models.AutoField(db_column='idproyeccion', primary_key=True)
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, db_column='idpelicula')
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, db_column='idsala')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='idedicion')
    fecha_hora = models.DateTimeField(db_column='fechahora')
    tiene_qa = models.BooleanField(db_column='tieneqa', default=False)
    aforo_disponible = models.IntegerField(db_column='aforodisponible', validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'proyecciones'

    def __str__(self):
        return f"{self.pelicula.titulo} en {self.sala.nombre_sala} ({self.fecha_hora})"


class EventoParalelo(models.Model):
    TIPO_CHOICES = [
        ('Masterclass', 'Masterclass'),
        ('Taller', 'Taller'),
        ('Coctel', 'Coctel'),
    ]

    id_evento = models.AutoField(db_column='idevento', primary_key=True)
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='idedicion')
    nombre_evento = models.CharField(db_column='nombreevento', max_length=150)
    tipo_evento = models.CharField(db_column='tipoevento', max_length=15, choices=TIPO_CHOICES)
    fecha_hora = models.DateTimeField(db_column='fechahora')
    aforo = models.IntegerField(db_column='aforo', validators=[MinValueValidator(1)])
    costo_inscripcion = models.DecimalField(db_column='costoinscripcion', max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    expositores = models.ManyToManyField(Personal, through='ExpositorEvento', related_name='eventos_paralelos')

    class Meta:
        db_table = 'eventosparalelos'

    def __str__(self):
        return self.nombre_evento


class ExpositorEvento(models.Model):
    evento = models.ForeignKey(EventoParalelo, on_delete=models.CASCADE, db_column='idevento', primary_key=True)
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, db_column='idpersonal')

    class Meta:
        db_table = 'expositorevento'
        unique_together = (('evento', 'personal'),)


class Categoria(models.Model):
    id_categoria = models.AutoField(db_column='idcategoria', primary_key=True)
    nombre_categoria = models.CharField(db_column='nombrecategoria', max_length=80)
    descripcion = models.CharField(db_column='descripcion', max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nombre_categoria


class MiembroJurado(models.Model):
    id_miembro = models.AutoField(db_column='idmiembro', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    profesion = models.CharField(db_column='profesion', max_length=60, blank=True, null=True)
    pais = models.CharField(db_column='pais', max_length=60, blank=True, null=True)
    email = models.CharField(db_column='email', max_length=100, blank=True, null=True)
    categorias = models.ManyToManyField(Categoria, through='JuradoCategoria', related_name='jurados')

    class Meta:
        db_table = 'miembrosjurado'

    def __str__(self):
        return self.nombre


class JuradoCategoria(models.Model):
    miembro = models.ForeignKey(MiembroJurado, on_delete=models.CASCADE, db_column='idmiembro', primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='idcategoria')

    class Meta:
        db_table = 'juradocategoria'
        unique_together = (('miembro', 'categoria'),)


class CompetenciaPelicula(models.Model):
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, db_column='idpelicula', primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='idcategoria')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='idedicion')

    class Meta:
        db_table = 'competenciapelicula'
        unique_together = (('pelicula', 'categoria', 'edicion'),)


class Evaluacion(models.Model):
    id_evaluacion = models.AutoField(db_column='idevaluacion', primary_key=True)
    miembro = models.ForeignKey(MiembroJurado, on_delete=models.CASCADE, db_column='idmiembro')
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, db_column='idpelicula')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='idcategoria')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='idedicion')
    puntuacion = models.IntegerField(db_column='puntuacion', validators=[MinValueValidator(1), MaxValueValidator(10)])
    comentario = models.TextField(db_column='comentario', blank=True, null=True)

    class Meta:
        db_table = 'evaluaciones'
        unique_together = (('miembro', 'pelicula', 'categoria', 'edicion'),)


class Premio(models.Model):
    id_premio = models.AutoField(db_column='idpremio', primary_key=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='idcategoria')
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE, db_column='idpelicula')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='idedicion')

    class Meta:
        db_table = 'premios'
        unique_together = (('categoria', 'edicion'),)


class Asistente(models.Model):
    TIPO_ASISTENTE_CHOICES = [
        ('General', 'General'),
        ('Prensa', 'Prensa'),
        ('Industria', 'Industria'),
        ('VIP', 'VIP'),
        ('Jurado', 'Jurado'),
    ]

    id_asistente = models.AutoField(db_column='idasistente', primary_key=True)
    nombre = models.CharField(db_column='nombre', max_length=100)
    email = models.CharField(db_column='email', unique=True, max_length=100)
    telefono = models.CharField(db_column='telefono', max_length=20, blank=True, null=True)
    tipo_asistente = models.CharField(db_column='tipoasistente', max_length=15, default='General', choices=TIPO_ASISTENTE_CHOICES)

    class Meta:
        db_table = 'asistentes'

    def __str__(self):
        return self.nombre


class Tarifa(models.Model):
    id_tarifa = models.AutoField(db_column='idtarifa', primary_key=True)
    nombre_tarifa = models.CharField(db_column='nombretarifa', max_length=30)
    precio = models.DecimalField(db_column='precio', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'tarifas'

    def __str__(self):
        return self.nombre_tarifa


class Entrada(models.Model):
    id_entrada = models.AutoField(db_column='identrada', primary_key=True)
    asistente = models.ForeignKey(Asistente, on_delete=models.CASCADE, db_column='idasistente')
    proyeccion = models.ForeignKey(Proyeccion, on_delete=models.CASCADE, db_column='idproyeccion', blank=True, null=True)
    evento = models.ForeignKey(EventoParalelo, on_delete=models.CASCADE, db_column='idevento', blank=True, null=True)
    tarifa = models.ForeignKey(Tarifa, on_delete=models.CASCADE, db_column='idtarifa')
    fecha_compra = models.DateTimeField(db_column='fechacompra', auto_now_add=True)

    class Meta:
        db_table = 'entradas'
        constraints = [
            models.CheckConstraint(
                condition=(
                    (models.Q(proyeccion__isnull=False, evento__isnull=True)) |
                    (models.Q(proyeccion__isnull=True, evento__isnull=False))
                ),
                name='ck_ent_destino'
            ),
            models.UniqueConstraint(
                fields=['asistente', 'proyeccion'],
                condition=models.Q(proyeccion__isnull=False),
                name='ux_ent_asiproy'
            ),
            models.UniqueConstraint(
                fields=['asistente', 'evento'],
                condition=models.Q(evento__isnull=False),
                name='ux_ent_asievt'
            )
        ]


class TipoAbono(models.Model):
    id_tipo_abono = models.AutoField(db_column='idtipoabono', primary_key=True)
    nombre_abono = models.CharField(db_column='nombreabono', max_length=60)
    descripcion = models.CharField(db_column='descripcion', max_length=200, blank=True, null=True)
    precio = models.DecimalField(db_column='precio', max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'tiposabono'

    def __str__(self):
        return self.nombre_abono


class Abono(models.Model):
    id_abono = models.AutoField(db_column='idabono', primary_key=True)
    asistente = models.ForeignKey(Asistente, on_delete=models.CASCADE, db_column='idasistente')
    tipo_abono = models.ForeignKey(TipoAbono, on_delete=models.CASCADE, db_column='idtipoabono')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='idedicion')
    fecha_compra = models.DateTimeField(db_column='fechacompra', auto_now_add=True)
    codigo_acceso = models.CharField(db_column='codigoacceso', unique=True, max_length=20)
    pagado = models.BooleanField(db_column='pagado', default=False)

    class Meta:
        db_table = 'abonos'
        unique_together = (('asistente', 'tipo_abono'),)


class Hotel(models.Model):
    id_hotel = models.AutoField(db_column='idhotel', primary_key=True)
    nombre_hotel = models.CharField(db_column='nombrehotel', max_length=100)
    direccion = models.CharField(db_column='direccion', max_length=200, blank=True, null=True)
    estrellas = models.IntegerField(db_column='estrellas', blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        db_table = 'hoteles'

    def __str__(self):
        return self.nombre_hotel


class Alojamiento(models.Model):
    id_alojamiento = models.AutoField(db_column='idalojamiento', primary_key=True)
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, db_column='idpersonal')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, db_column='idhotel')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='idedicion')
    nro_habitacion = models.CharField(db_column='nrohabitacion', max_length=10)
    check_in = models.DateField(db_column='checkin')
    check_out = models.DateField(db_column='checkout')

    class Meta:
        db_table = 'alojamientos'


class Traslado(models.Model):
    TIPO_TRASLADO_CHOICES = [
        ('Vuelo', 'Vuelo'),
        ('Transfer', 'Transfer'),
    ]

    id_traslado = models.AutoField(db_column='idtraslado', primary_key=True)
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, db_column='idpersonal')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='idedicion')
    tipo_traslado = models.CharField(db_column='tipotraslado', max_length=10, choices=TIPO_TRASLADO_CHOICES)
    origen = models.CharField(db_column='origen', max_length=100)
    destino = models.CharField(db_column='destino', max_length=100)
    fecha_hora = models.DateTimeField(db_column='fechahora')
    nro_vuelo = models.CharField(db_column='nrovuelo', max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'traslados'


class Patrocinador(models.Model):
    id_patrocinador = models.AutoField(db_column='idpatrocinador', primary_key=True)
    nombre_empresa = models.CharField(db_column='nombreempresa', max_length=100)
    contacto = models.CharField(db_column='contacto', max_length=100, blank=True, null=True)
    email = models.CharField(db_column='email', max_length=100, blank=True, null=True)
    redes_sociales = models.CharField(db_column='redessociales', max_length=150, blank=True, null=True)

    class Meta:
        db_table = 'patrocinadores'

    def __str__(self):
        return self.nombre_empresa


class PatrocinioEdicion(models.Model):
    TIPO_APORTE_CHOICES = [
        ('Economico', 'Economico'),
        ('Especie', 'Especie'),
    ]

    id_patrocinio = models.AutoField(db_column='idpatrocinio', primary_key=True)
    patrocinador = models.ForeignKey(Patrocinador, on_delete=models.CASCADE, db_column='idpatrocinador')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='idedicion')
    tipo_aporte = models.CharField(db_column='tipoaporte', max_length=10, choices=TIPO_APORTE_CHOICES)
    monto = models.DecimalField(db_column='monto', max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    descripcion_aporte = models.CharField(db_column='descripcionaporte', max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'patrocinioedicion'
